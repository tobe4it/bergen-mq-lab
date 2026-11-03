# Standalone MQSC deployment (GNU/Linux, AIX, Windows)

This feature does **not** provision IBM MQ, Proxmox, Podman, REST endpoints or queue
managers. It uses an existing local IBM MQ installation on each target and the native
`runmqsc` executable. MQSC input may contain multiple DEFINE, DELETE, ALTER,
DELETE/DEFINE or other MQSC statements in source order. MQSC is **not transactional**;
an unsuccessful deployment may have applied preceding commands.

## IBM MQ version coverage

The deployment architecture explicitly targets IBM MQ **9.2, 9.3, 9.4 and
10.0**, including applicable LTS and Continuous Delivery maintenance levels.
IBM MQ 10.0 LTS became available in June 2026 and MQ 10.0.1 CD in October
2026. This is an architectural scope statement, **not a claim that the
adapter has passed live compatibility tests** for these releases.

Select the correct host-native MQ installation and `runmqsc` binary for
each queue manager. Detect and record the actual MQ version and platform as
part of target acceptance; do not infer the running version from the declared
inventory label alone. Validate the particular MQSC attributes and commands
against that release. Run `audit`, `validate`, an approved disposable
end-to-end apply test, and error/partial-execution tests before certifying a
version/platform combination. Do not automatically upgrade older managers.

IBM references:
- [MQ 10.0 MQSC administration](https://www.ibm.com/docs/en/ibm-mq/10.0.x?topic=administering-mq-using-mqsc-commands)
- [MQ 10.0 changes](https://www.ibm.com/docs/en/ibm-mq/10.0.x?topic=1000-whats-changed-in-mq)
- [MQ 10.0 LTS fix list](https://www.ibm.com/support/pages/fix-list-ibm-mq-100-lts)

## Prerequisites

Install Ansible and `ansible.windows` on the controller, configure SSH for Linux
and AIX or WinRM/PSRP for Windows, and provide an account permitted to administer
the selected queue manager. Use Ansible Vault for credentials, not Git. For MQ
multi-installation systems set `mqsc_runmqsc` to the executable belonging to the
right installation. The user running `runmqsc` must have appropriate MQ authorities.
AIX and Linux can use `mqsc_become: true` and `mqsc_become_user: mqm`;
Windows uses the authenticated connection identity.

Use a **site-local** inventory containing an `mqsc_targets` group. Start from
`ansible/examples/mqsc-inventory.yml`. Limit the target to exactly one host with
`--limit` for each invocation. A source file and change ID are required.
Do not use production credentials or production targets during evaluation.

## Commands

```bash
ansible-playbook -i inventory.local.yml ansible/playbooks/mqsc-deploy.yml \
  --limit linux-mq -e mqsc_source=ansible/mqsc/examples/sample.mqsc \
  -e mqsc_change_id=DEMO-001 -e mqsc_mode=audit

ansible-playbook -i inventory.local.yml ansible/playbooks/mqsc-deploy.yml \
  --limit linux-mq -e mqsc_source=ansible/mqsc/examples/sample.mqsc \
  -e mqsc_change_id=DEMO-001 -e mqsc_mode=validate

# Only after reviewing input and validation:
ansible-playbook -i inventory.local.yml ansible/playbooks/mqsc-deploy.yml \
  --limit linux-mq -e mqsc_source=ansible/mqsc/examples/sample.mqsc \
  -e mqsc_change_id=DEMO-001 -e mqsc_mode=apply \
  -e mqsc_confirm_apply=true
```

`audit` only checks that the executable exists; it does **not** copy a file or
connect to a queue manager. `validate` stages the file and invokes `runmqsc -v`;
this checks syntax only, not object existence, permissions or semantic success.
`apply` first validates then invokes `runmqsc` with the original file.
Failures include a nonzero return code or IBM MQ AMQxxxxE/AMQxxxxS messages.
Review the full evidence even for successful return codes and warnings.

Evidence is written as protected JSON to `ansible/reports/mqsc/` (Git-ignored),
including source SHA-256, return code and command output. MQSC files and MQ output
may contain sensitive details: protect controller storage, staging directories,
Windows ACLs and remote access. **Windows staging ACLs must be restricted by the
site administrator before deploying sensitive MQSC files.** Outputs are not
redacted. The change ID names the remote staging file; reusing it overwrites that
file. There is no automatic rollback, once-only ledger, or concurrent lock.
Coordinate deployment serialization externally and do not blindly replay a
partially successful change.

Some MQ installations, especially containerized MQ-Lab instances, require
`podman exec`/container-specific execution rather than host-native `runmqsc`.
This standalone role deliberately targets host-native installations; a separate
container adapter can be added without changing the MQSC file format.
