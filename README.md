# Bergen MQ Lab

Reproducible IBM MQ 9.4 LTS evaluation lab built with Ansible, Rocky Linux 9
LXC guests, Podman and strict safety gates.

This repository is **evaluation only**. It is not approved for productive IBM
MQ operation. Review the applicable IBM terms before accepting the explicit
license gate or deploying an IBM MQ image.

## Scope

- Provision two isolated MQ queue-manager guests and one separate Java client.
- Run MQ containers through Podman/Quadlet in unprivileged Proxmox LXCs.
- Enforce TLS verification, pinned container image identities and explicit
  mutation gates.
- Configure LDAP trust without weakening certificate validation.
- Reconcile a bounded set of MQ objects through the administrative REST API.
- Exercise local messaging, authentication and two-QMgr topology checks.
- Produce guarded, sanitized audit evidence.

No IBM MQ image, MQ client library, credential, private key, certificate
private key or site-local inventory is stored in Git.

## Repository layout

```text
ansible/
  examples/       Site-local topology examples
  library/        Custom Ansible modules
  module_utils/   REST reconciliation and audit implementation
  playbooks/      Provisioning, configuration and verification workflows
  roles/          MQ server, MQ client and remote-syslog roles
docs/             Architecture, deployment and validation guides
tests/            Offline and opt-in Ansible integration tests
tools/mq-tests/   Java messaging probe
```

## Quick validation

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
python3 -m unittest discover -s tests -v

for playbook in ansible/playbooks/*.yml; do
  ansible-playbook -i localhost, "$playbook" --syntax-check
done
```

The full-runtime tests are opt-in because they require local Ansible RPC/IPC:

```bash
BERGEN_MQ_RUN_ANSIBLE_INTEGRATION=1 \
  python3 -m unittest discover -s tests -v
```

## Deployment

Start with [the MQ lab guide](docs/MQ-LAB.md) and copy the provided example
inventory and variable files. Keep all site-local values and Vault material in
the ignored local files.

The provisioning workflows include the generic LXC lifecycle and remote
syslog components required by this lab, so the repository does not depend on a
checkout of Bergen Platform.

## Origin

The lab was extracted from
[`tobe4it/bergen-platform`](https://github.com/tobe4it/bergen-platform) after
release v0.10.0. The original commits remain available in that repository;
this repository starts with a reviewed standalone snapshot and records its
source revision in [MIGRATION.md](MIGRATION.md).

