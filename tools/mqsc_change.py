#!/usr/bin/env python3
"""Plan and execute one numbered MQSC change through the standalone Ansible role."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import yaml


ROOT = Path(__file__).resolve().parents[1]
SERIES = ("9.2", "9.3", "9.4", "10.0")
ALIAS = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,79}")
CHANGE = re.compile(r"C[0-9]{8}")


class ManifestLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        result = super().construct_mapping(node, deep=deep)
        if len(result) != len(node.value):
            raise ValueError("Duplicate manifest key")
        return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(content):
    return hashlib.sha256(content).hexdigest()


def read_change(path, root):
    if path.resolve() != path or not path.is_file():
        raise ValueError(f"Expected a regular change file under {root}: {path}")
    data = path.read_bytes()
    if not 0 < len(data) <= 1048576 or not data.strip():
        raise ValueError(f"Expected nonempty MQSC of at most 1 MiB: {path}")
    if re.search(rb"[^\x09\x0a\x20-\x7e]", data) or not data.endswith(b"\n"):
        raise ValueError(f"Numbered MQSC requires ASCII text with LF line endings: {path}")
    return data


def load_plan(root, change, target):
    if not CHANGE.fullmatch(change):
        raise ValueError("Expected change ID C########")
    manifest = root / "changes" / f"{change}.yml"
    shared = root / "changes" / f"{change}.mqsc"
    individual = {p.parent.name: p for p in root.glob(f"*/{change}.mqsc") if p != shared}
    allowed = list(SERIES)
    if manifest.exists():
        if manifest.resolve() != manifest or not manifest.is_file():
            raise ValueError(f"Expected a regular manifest file: {manifest}")
        if target is not None:
            raise ValueError("A manifest defines the complete target scope; omit --target")
        definition = yaml.load(manifest.read_text(encoding="utf-8"), Loader=ManifestLoader)
        if not isinstance(definition, dict) or not {"targets"} <= definition.keys() <= {
            "targets", "mq_series"
        }:
            raise ValueError("Manifest requires targets and optionally mq_series")
        targets = definition["targets"]
        allowed = definition.get("mq_series", allowed)
    else:
        if target is None or set(individual) != {target} or shared.exists():
            raise ValueError("Specify --target for a unique per-target change, or provide a manifest")
        targets = [target]
    if (
        not isinstance(targets, list)
        or not targets
        or any(not isinstance(t, str) or not ALIAS.fullmatch(t) or t == "changes" for t in targets)
        or len(set(targets)) != len(targets)
    ):
        raise ValueError("Expected a nonempty list of distinct inventory aliases")
    if (
        not isinstance(allowed, list)
        or not allowed
        or any(s not in SERIES for s in allowed)
        or len(set(allowed)) != len(allowed)
    ):
        raise ValueError("mq_series must list distinct strings from 9.2, 9.3, 9.4, 10.0")
    if set(individual) - set(targets) or (shared.exists() and set(targets) <= set(individual)):
        raise ValueError("Change ID has unreferenced MQSC files")
    files = {alias: individual.get(alias, shared) for alias in targets}
    payloads = {alias: read_change(path, root) for alias, path in files.items()}
    entries = [
        {"target": alias, "file": str(files[alias].relative_to(root)), "sha256": digest(payloads[alias])}
        for alias in targets
    ]
    return {"change": change, "mq_series": allowed, "targets": entries}, payloads


def write_private(path, data):
    with path.open("xb") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(data)


def run_target(args, plan, entry, source, phase, report_dir, expected=None):
    alias = entry["target"]
    variables = {
        "mqsc_change_target": alias,
        "mqsc_change_id": plan["change"],
        "mqsc_source": str(source),
        "mqsc_mode": phase,
        "mqsc_allowed_series": plan["mq_series"],
        "mqsc_confirm_apply": phase == "apply",
        "mqsc_expected_identity": expected,
        "mqsc_phase_report": str(report_dir / f"{alias}.{phase}.json"),
    }
    vars_file = source.parent / "vars.json"
    vars_file.write_bytes(canonical(variables))
    log_path = report_dir / f"{alias}.{phase}.log"
    with log_path.open("xb") as log:
        os.fchmod(log.fileno(), 0o600)
        result = subprocess.run(
            ["ansible-playbook", "-i", str(args.inventory), "--limit", alias,
             str(ROOT / "ansible/playbooks/mqsc-change.yml"), "-e", f"@{vars_file}"],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    evidence_path = Path(variables["mqsc_phase_report"])
    evidence = json.loads(evidence_path.read_text()) if evidence_path.is_file() else {}
    evidence.update({
        "success": result.returncode == 0 and evidence.get("success") is True,
        "ansible_rc": result.returncode,
        "log": log_path.name,
    })
    return evidence


def execute(args):
    plan, payloads = load_plan(args.changes.resolve(), args.change, args.target)
    args.inventory = args.inventory.resolve(strict=True)
    inventory_sha = digest(args.inventory.read_bytes())
    plan.update(inventory=str(args.inventory), inventory_sha256=inventory_sha)
    plan_sha = digest(canonical(plan))
    if args.mode == "apply":
        if args.approve_sha256 != plan_sha or not args.approval_ref or not args.approval_ref.strip():
            raise ValueError(f"Apply requires --approve-sha256 {plan_sha} and --approval-ref")
    elif args.approve_sha256 or args.approval_ref:
        raise ValueError("Approval arguments are only accepted for apply")

    args.reports.mkdir(mode=0o700, parents=True, exist_ok=True)
    report_dir = Path(tempfile.mkdtemp(prefix=f"{args.change}-", dir=args.reports.resolve()))
    write_private(report_dir / "plan.json", canonical({
        **plan, "plan_sha256": plan_sha, "mode": args.mode, "approval_ref": args.approval_ref
    }))
    print(f"Plan SHA256 {plan_sha}\nEvidence {report_dir}", flush=True)
    entries = plan["targets"]
    outcomes = {entry["target"]: {} for entry in entries}

    with tempfile.TemporaryDirectory(prefix="mqsc-input-") as directory:
        sources = {alias: Path(directory) / f"{alias}.mqsc" for alias in payloads}
        for alias, source in sources.items():
            write_private(source, payloads[alias])

        def run(entry, phase, expected=None):
            alias = entry["target"]
            try:
                if digest(args.inventory.read_bytes()) != inventory_sha:
                    raise ValueError("Inventory changed since planning")
                evidence = run_target(args, plan, entry, sources[alias], phase, report_dir, expected)
            except (OSError, ValueError) as error:
                evidence = {"success": False, "error": str(error)}
            outcomes[alias][phase] = evidence
            write_private(report_dir / f"{alias}.result-{phase}.json", canonical({
                **entry, "change": args.change, "plan_sha256": plan_sha, "phase": phase, **evidence
            }))
            print(f"{alias} {phase} {'ok' if evidence['success'] else 'failed'}", flush=True)
            return evidence["success"]

        preflight = "validate" if args.mode == "apply" else args.mode
        results = [run(entry, preflight) for entry in entries]
        success = all(results)
        if args.mode == "apply":
            for entry in entries:
                alias = entry["target"]
                if success:
                    success = run(entry, "apply", outcomes[alias]["validate"]["identity"])
                else:
                    outcomes[alias]["apply"] = {"success": False, "status": "blocked"}
                    write_private(report_dir / f"{alias}.result-apply.json", canonical({
                        **entry, "change": args.change, "plan_sha256": plan_sha,
                        "phase": "apply", **outcomes[alias]["apply"],
                    }))
                    print(f"{alias} apply blocked", flush=True)
    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("change", help="C########")
    parser.add_argument("-i", "--inventory", type=Path, required=True)
    parser.add_argument("--target", help="Inventory alias for a per-target change")
    parser.add_argument("--changes", type=Path, default=ROOT / "mqsc")
    parser.add_argument("--reports", type=Path, default=ROOT / "ansible/reports/mqsc")
    parser.add_argument("--mode", choices=("audit", "validate", "apply"), default="audit")
    parser.add_argument("--approve-sha256")
    parser.add_argument("--approval-ref")
    try:
        return execute(parser.parse_args())
    except (OSError, ValueError, yaml.YAMLError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    sys.exit(main())
