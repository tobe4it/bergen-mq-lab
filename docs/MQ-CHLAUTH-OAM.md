# MQ CHLAUTH/OAM: staged safety and negative tests

Historical source: `tobe4it/bergen-platform#42`. This package is
**evaluation-lab development**. Its many offline CHLAUTH safety models do
not grant permission to modify any queue manager, LDAP server or firewall.

Contents:
- CHLAUTH read-only evidence collectors, channel-status cross-checks,
  desired-state planning, bounded MQSC parser and write-contract review.
- Offline-only journal, staged execution simulation, explicit recovery
  triage and fail-closed cleanup of run-owned test fixtures.
- LDAP/OAM preflight, group smoke and separately gated provisioning
  playbooks; do not invoke provisioning in a live environment until
  inventory, identities, backups, rollback and security authority have
  been independently reviewed.
- Synthetic negative regression tests for parsing, collisions, journal
  state, status mismatch, partial rollback and unauthorized writes.

Never treat a test's placeholder IP or user identity as a deployable site
configuration. The original `ansible/host_vars/bergen-mq-lab*.yml`
files were intentionally **not copied** from the legacy repository;
all live endpoints, certificates, LDAP users and access controls must
come from ignored site-local inventory/Vault.

Dependencies: the dedicated mTLS transport PR #2; the transport PKI
PR #1 is also required for positive live TLS tests. No action on MQ,
CHLAUTH, OAM, LDAP or network services is performed by merging this
code. Source QMgr name and hardening must be checked before deployment.

Remaining gates: full controller Python regression suite, Ansible syntax,
read-only live A/B CHSTATUS/CHLAUTH and LDAP audit, user-group OAM
negative/positive scenarios, forced-failure rollback and audit of real
MQ 9.4 REST responses. No MQ service restarts authorized.
