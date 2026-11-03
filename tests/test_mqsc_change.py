"""Exercise the numbered workflow through Ansible without connecting to IBM MQ."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
CHANGE = "C00000042"


@pytest.fixture
def lab(tmp_path, monkeypatch):
    if not shutil.which("ansible-playbook"):
        pytest.skip("ansible-playbook required")
    monkeypatch.setenv("ANSIBLE_REMOTE_TEMP", str(tmp_path / "ansible-tmp"))
    install = tmp_path / "mq"
    binaries = install / "bin"
    binaries.mkdir(parents=True)
    uname = binaries / "uname"
    uname.write_text("#!/bin/sh\nprintf 'Linux\\n'\n")
    uname.chmod(0o700)
    monkeypatch.setenv("PATH", str(binaries) + os.pathsep + os.environ["PATH"])
    trace = tmp_path / "applied"
    for name, body in {
        "dspmq": """
import sys
qmgr = sys.argv[sys.argv.index('-m') + 1]
version = {'QM2': '9.4.0.0', 'QM92': '9.2.0.0', 'QM93': '9.3.0.0'}.get(qmgr, '10.0.1.0')
print(f'QMNAME({qmgr}) STATUS(Running) INSTNAME(Installation1) INSTPATH({root}) INSTVER({version})')
raise SystemExit(5)
""",
        "runmqsc": """
import sys
payload = sys.stdin.read()
qmgr = sys.argv[-1]
if payload == 'DISPLAY QMGR VERSION\\n':
    version = {'QM2': '09040000', 'QM92': '09020000', 'QM93': '09030000'}.get(qmgr, '10000100')
    print(f'   QMNAME({qmgr}) VERSION({version})')
elif '-v' in sys.argv:
    if 'INVALID' in payload:
        print('AMQ8405E: Syntax error')
        raise SystemExit(10)
else:
    with open(trace, 'a') as f:
        f.write(qmgr + ':' + payload)
""",
    }.items():
        path = binaries / name
        path.write_text(f"#!{sys.executable}\nroot = {str(install)!r}\ntrace = {str(trace)!r}\n" + body)
        path.chmod(0o700)

    inventory = tmp_path / "inventory.yml"
    hosts = {
        alias: {
            "ansible_connection": "local",
            "ansible_python_interpreter": sys.executable,
            "mqsc_platform": "linux",
            "mqsc_installation": str(install),
            "mqsc_qmgr": qmgr,
        }
        for alias, qmgr in [("target-a", "QM1"), ("target-b", "QM2")]
    }
    inventory.write_text(yaml.safe_dump({"mqsc_targets": {"hosts": hosts}}))
    changes = tmp_path / "mqsc"
    for folder in ("changes", "target-b"):
        (changes / folder).mkdir(parents=True)
    (changes / "changes" / f"{CHANGE}.yml").write_text("targets: [target-a, target-b]\n")
    (changes / "changes" / f"{CHANGE}.mqsc").write_text("DEFINE QLOCAL(A) DESCR('{{ literal }}')\n")
    override = changes / "target-b" / f"{CHANGE}.mqsc"
    override.write_text("DEFINE QLOCAL(B)\n")

    def run(*args, ok=True):
        reports = tmp_path / "reports"
        cmd = [sys.executable, str(ROOT / "tools/mqsc_change.py"), CHANGE,
               "-i", str(inventory), "--changes", str(changes), "--reports", str(reports)]
        result = subprocess.run([*cmd, *args], capture_output=True, text=True, check=False)
        assert (result.returncode == 0) is ok, result.stdout + result.stderr
        if "Evidence " not in result.stdout:
            return result, None
        evidence = Path(next(line[9:] for line in result.stdout.splitlines() if line.startswith("Evidence ")))
        if ok:
            assert evidence.stat().st_mode & 0o777 == 0o700
        return result, evidence

    return run, trace, override, inventory, binaries


def test_apply_scope_preflight_and_evidence(lab):
    run, trace, override, _, _ = lab
    _, audit = run()
    plan = json.loads((audit / "plan.json").read_text())
    result = json.loads((audit / "target-a.result-audit.json").read_text())
    assert result["identity"]["version"] == "10.0.1.0"
    assert set(result["commands"]) == {"discovery", "connection"}
    _, evidence = run("--mode", "apply", ok=False)
    assert evidence is None
    approve = ("--mode", "apply", "--approve-sha256", plan["plan_sha256"], "--approval-ref", "TEST-42")
    _, applied = run(*approve)
    assert (applied / "target-b.result-apply.json").exists()
    assert trace.read_text() == "QM1:DEFINE QLOCAL(A) DESCR('{{ literal }}')\nQM2:DEFINE QLOCAL(B)\n"

    trace.unlink()
    override.write_text("INVALID\n")
    _, evidence = run(*approve, ok=False)
    assert evidence is None
    _, audit = run()
    plan = json.loads((audit / "plan.json").read_text())
    _, blocked = run("--mode", "apply", "--approve-sha256", plan["plan_sha256"],
                     "--approval-ref", "TEST-43", ok=False)
    assert not trace.exists()
    result = json.loads((blocked / "target-b.result-validate.json").read_text())
    assert result["commands"]["validate"]["rc"] == 10
    for alias in ("target-a", "target-b"):
        result = json.loads((blocked / f"{alias}.result-apply.json").read_text())
        assert result["status"] == "blocked"


def test_plan_rejects_duplicate_id_and_manifest_keys(tmp_path):
    sys.path.insert(0, str(ROOT / "tools"))
    from mqsc_change import load_plan

    for alias in ("a", "b"):
        (tmp_path / alias).mkdir()
        (tmp_path / alias / f"{CHANGE}.mqsc").write_text("DISPLAY QMGR\n")
    with pytest.raises(ValueError, match="unique per-target"):
        load_plan(tmp_path, CHANGE, "a")
    (tmp_path / "changes").mkdir()
    manifest = tmp_path / "changes" / f"{CHANGE}.yml"
    manifest.write_text("targets: [a]\ntargets: [b]\n")
    with pytest.raises(ValueError, match="Duplicate"):
        load_plan(tmp_path, CHANGE, None)

@pytest.mark.parametrize(("engine", "series"), [("podman", "9.2"), ("docker", "9.3")])
def test_container_audit_uses_running_container_id(lab, engine, series):
    run, trace, _, inventory, binaries = lab
    container_id = "a" * 64
    runtime = binaries / engine
    runtime.write_text(f"""#!{sys.executable}
import json
import os
import sys
args = sys.argv[1:]
if args == ['container', 'inspect', 'mq-test']:
    print(json.dumps([{{'Id': {container_id!r}, 'State': {{'Running': True}}}}]))
elif args[:3] == ['exec', '-i', {container_id!r}]:
    os.execv(args[3], args[3:])
else:
    raise SystemExit(1)
""")
    runtime.chmod(0o700)
    data = yaml.safe_load(inventory.read_text())
    data["mqsc_targets"]["hosts"]["target-a"].update(
        mqsc_runtime=engine, mqsc_container="mq-test", mqsc_qmgr="QM" + series.replace(".", "")
    )
    inventory.write_text(yaml.safe_dump(data))

    _, evidence = run()
    result = json.loads((evidence / "target-a.result-audit.json").read_text())
    assert result["identity"]["container_id"] == container_id
    assert result["identity"]["runtime"] == engine
    assert result["identity"]["version"] == series + ".0.0"
    assert not trace.exists()
