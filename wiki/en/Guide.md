# Bergen MQ Lab — Operations and Reference Guide

> This guide documents the evaluation lab and the separate standalone MQSC deployment adapter. The lab is evaluation-only and not certified for production. The adapter targets existing host-native IBM MQ installations; it is not a substitute for change approval or qualification on the target MQ version.

## Contents

1. Overview and scope
2. Architecture
3. Requirements
4. Installation
5. Configuration
6. MQSC deployment
7. Declarative object administration
8. TLS, LDAP and authorizations
9. Auditing and tests
10. Operations and troubleshooting
11. Backup, recovery and rollback
12. Security, governance and limitations

## 1. Overview and scope

The lab provisions two isolated IBM MQ evaluation queue managers and one Java client using Ansible, Proxmox LXC, Rocky Linux and Podman/Quadlet. The standalone MQSC adapter targets existing GNU/Linux, AIX or Windows hosts without provisioning MQ. Do not confuse the REST reconciler's bounded object model with unrestricted MQSC execution.

The README is the starting point. See `docs/MQ-LAB.md`, `docs/MQ.md`, `docs/MQ-TOPOLOGY.md` and `docs/MQSC-DEPLOY.md` for authoritative detail.

## 2. Architecture

The controller orchestrates Proxmox guests using SSH and Ansible. MQ container instances keep persistent data outside the container and expose an authenticated HTTPS administrative interface. The second queue manager and Java client are isolated test entities; external firewall and access rules are separately managed.

The standalone MQSC workflow uses SSH on GNU/Linux/AIX or WinRM/PSRP on Windows, stages a local MQSC file and invokes the MQ installation's `runmqsc` executable on the target host.

## 3. Requirements

For lab provisioning prepare a Proxmox host, Rocky Linux 9 LXC template, Podman/Quadlet support, Ansible and the collections in `requirements.yml`. Configure site-local inventories, accessible repositories, trusted SSH host keys, appropriate network ACLs and a valid IBM evaluation entitlement.

For standalone MQSC, use an existing IBM MQ installation, `runmqsc` appropriate to that installation, target operating-system connectivity and a permitted MQ administrator account. Do not assume that developer image licensing grants production use.

## 4. Installation

Copy the example variables into local ignored files, review every site value, store credentials with Ansible Vault, and set the explicit evaluation and IBM license gates only after reviewing applicable terms. Run `ansible/playbooks/deploy-mq-lab.yml` for first-time provisioning. Use `bootstrap-mq-lab.yml` for subsequent configuration reconciliation.

Do not rerun first-time provisioning against an unknown guest or address. Verify VMID uniqueness, identity, persistence and inventories before any operation. The independent MQSC adapter never installs IBM MQ.

## 5. Configuration

Keep site addresses, Proxmox VMIDs, TLS endpoints, MQ names and credentials outside Git. The repository ships example inventories under `ansible/examples/` and configuration examples under `ansible/vars/` and `ansible/group_vars/`. Review the selected target variables before deployment.

For MQSC set `mqsc_platform`, `mqsc_qmgr`, `mqsc_runmqsc` when the installation path is nondefault, `mqsc_source`, and a unique `mqsc_change_id`. Use exactly one target host per invocation.

## 6. MQSC deployment

Run `ansible/playbooks/mqsc-deploy.yml` with `mqsc_mode=audit` first, then `mqsc_mode=validate`, and only after peer review `mqsc_mode=apply -e mqsc_confirm_apply=true`. A source MQSC file can contain DEFINE, DELETE, ALTER and other supported MQSC commands in execution order.

`audit` checks for the executable only; `validate` uses `runmqsc -v` for syntax checks, not semantic or authority validation. MQSC changes are not transactional. Review full output and partial results; no automatic rollback, duplicate prevention or queue-manager lock is implemented. Protect Windows staging ACLs yourself.

## 7. Declarative object administration

`ansible/library/mq_objects.py` and the REST reconciler manage a bounded set of queue, channel, topic and namelist attributes using HTTPS and real-state comparison. Missing YAML declarations are not pruned. Check mode and diff are supported for that bounded model.

Use `ansible/playbooks/mq-objects.yml --check --diff` with a reviewed, Vault-backed local variables file before applying. CHLAUTH/OAM, queue-manager lifecycle and unrestricted MQSC are not supplied by this module; use the standalone adapter where appropriate.

## 8. TLS, LDAP and authorizations

Keep certificate verification enabled for REST and MQ transport. The lab uses a private evaluation CA with a distinct service certificate and separate protected private keys; do not commit certificates or keys. Client/peer trust, CHLAUTH, CONNAUTH, LDAP and OAM need independent review.

Never disable hostname verification, broaden firewall ranges or grant `mqm` administrator rights merely to pass a test. Validate denied-access cases in a disposable lab and keep production policies outside automatic evaluation changes.

## 9. Auditing and tests

Run `python3 -m unittest discover -s tests -v` and Ansible syntax checks. The single-QMgr audit playbook uses explicit test mutation gates and records scoped evidence with SHA-256 integrity markers. Additional topology checks must be assessed independently.

Offline and mock tests are not proof of IBM MQ platform compatibility. Mark unsupported or unexecuted live cases NOT TESTED; record exact target version, operating system, Git revision, outcome and artifacts in acceptance reports.

## 10. Operations and troubleshooting

Diagnose controller connectivity, target OS connection identity, queue-manager state, MQ installation selection, certificate chain, MQ authority and log output in that order. Check `journalctl -u bergen-mq-lab.service` on lab hosts and relevant MQ error logs.

For REST HTTP 401/403, verify identity, CA trust and required CSRF token rather than disabling checks. For MQSC failures, inspect protected report JSON under `ansible/reports/mqsc/` and never blindly replay a partially applied change.

## 11. Backup, recovery and rollback

Preserve persistent MQ queue-manager data, configuration, certificates and off-host backups according to local policy. Container recreation does not imply data deletion, but it is not a backup. Take a verified recovery point before destructive changes.

MQSC has no general transaction or automatic rollback. Build a reviewed reverse change plan and verify object state before retrying. Restore testing, host reboot and recovery-time objectives must be validated separately in a disposable environment.

## 12. Security, governance and limitations

All example systems are evaluation-only. Production usage requires independent IBM licensing, security, change control and compatibility approval. Store Vault secrets, reports and staged MQSC inputs securely. Changes must be peer reviewed, narrowly scoped and attributable to a change ID.

The current standalone adapter does not handle containerized MQ on the host, IBM MQ versions without required `runmqsc` options, cross-host concurrency locks or exactly-once execution. An external release process should enforce approval, windows, backups and target-specific acceptance.

---

Canonical technical references: [README](https://github.com/tobe4it/bergen-mq-lab/blob/main/README.md) · [Lab](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-LAB.md) · [REST](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ.md) · [MQSC](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md) · [Audit](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-AUDIT.md) · [Topology](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-TOPOLOGY.md).
