# Numbered MQSC changes

Use this workflow with existing queue managers on native GNU/Linux, AIX and
Windows, or in GNU/Linux Podman and Docker containers. It requires neither
MQ provisioning nor the lab's REST API.

## Inventory and change files

Install the Python and Ansible dependencies from the repository root.

~~~sh
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
~~~

Edit the local inventory and remove unused example hosts. Define one inventory
alias per queue manager in the `mqsc_targets` group. Set `ansible_host`,
`ansible_user`, the connection settings, `mqsc_qmgr` and `mqsc_platform`.
Use SSH for GNU/Linux and AIX, or WinRM/PSRP with the corresponding controller
dependencies for Windows. Keep credentials in Vault or the connection credential
store. Use a dedicated MQ administration identity. On POSIX, `mqsc_become`
and `mqsc_become_user` select the identity that invokes MQ or the container
engine. Windows uses its connection identity.

Set `mqsc_installation` to the exact root reported by MQ if it differs from
`/opt/mqm` on Linux, `/usr/mqm` on AIX or `C:\Program Files\IBM\MQ` on
Windows. For a GNU/Linux container, set `mqsc_runtime: podman` or
`mqsc_runtime: docker` and `mqsc_container`. The installation path is then
inside the container. The selected host identity must be able to inspect and
execute commands in the container. Its default execution user must be authorized
for MQ administration.

Assign each change a globally unique `C########` ID. Each invocation selects
one ID. MQSC files contain portable ASCII text up to 1 MiB with LF line endings.

- Single target. Use `mqsc/<inventory-alias>/C00000001.mqsc` and pass
  `--target <inventory-alias>`.
- Multiple targets. Use `mqsc/changes/C00000002.yml` with an ordered
  `targets` list. A target-specific file takes precedence over the optional
  shared `mqsc/changes/C00000002.mqsc`. Every listed target needs one
  effective file. An optional `mq_series` list restricts the allowed MQ series.

~~~yaml
targets: [linux-mq, podman-mq]
mq_series: ['9.4', '10.0']
~~~

The examples in [mqsc](../mqsc) use read-only MQSC. Keep one inventory alias per
actual deployment endpoint and queue manager. Treat the inventory, Ansible
configuration, associated variables and change repository as trusted release inputs.

## Run and approve

~~~sh
python3 tools/mqsc_change.py C00000001 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq
python3 tools/mqsc_change.py C00000002 -i ansible/inventory.mqsc.local.yml \
  --mode validate
python3 tools/mqsc_change.py C00000002 -i ansible/inventory.mqsc.local.yml \
  --mode apply --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
~~~

- **Audit** is the default. It checks the host platform, the selected engine
  and running container when applicable, and the running queue manager's
  installation path and version. It compares `dspmq` installation metadata
  with `DISPLAY QMGR VERSION` on the live manager. MQ 9.2, 9.3, 9.4 and
  10.0 are accepted, including 10.0.1 CD, subject to the manifest restriction.
  Audit only sends the workflow's own read-only MQSC query.
- **Validate** runs audit and sends the change to `runmqsc -v`. This checks
  syntax against the target release. It cannot establish object existence,
  apply authorization or semantic success.
- **Apply** requires the SHA-256 of the reviewed plan and an approval reference
  from the site's change process. The plan binds ordered targets, file hashes,
  allowed series and the inventory file path and hash. Review any external
  inventory variables and connection settings as part of the same approval.
  The controller validates every target before it sends any change. It then
  rechecks identity and syntax on each target and applies in order, stopping
  after the first apply failure. The approval reference is recorded for audit.
  The workflow relies on the site's process to authenticate the approver.

Every run creates a private directory under `ansible/reports/mqsc/` with the
plan, per-target and per-phase JSON results, and Ansible logs. Reports include
the source hash, detected identity and MQ return codes and output when available.
Targets that cannot connect or are blocked by preflight still get an outcome.
Logs and reports can contain sensitive details. Store them accordingly.

MQSC can partially apply commands before returning an error. Inspect the
manager's state and evidence before retrying. Arrange serialization of
independent runs and rollback through the site's change process. The supported
series and adapters are tested with simulators in CI. Qualify the exact MQ
release, platform, container image and authorities in a disposable environment
before relying on them for live changes.

## Existing single-target playbook

`ansible/playbooks/mqsc-deploy.yml` retains the original native interface
using `--limit`, `mqsc_source`, `mqsc_change_id`, `mqsc_mode`,
`mqsc_runmqsc` and `mqsc_confirm_apply`. It uses remote file staging
and its original single-target gates. The numbered workflow is invoked through
`tools/mqsc_change.py`.

IBM references

- [MQSC administration and runmqsc verification](https://www.ibm.com/docs/en/ibm-mq/10.0.x?topic=amumc-running-mqsc-commands-from-text-files-under-runmqsc)
- [dspmq status and installation discovery](https://www.ibm.com/docs/en/ibm-mq/10.0.x?topic=reference-dspmq-display-queue-managers)
