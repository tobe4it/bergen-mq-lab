# Single-QMgr audit (example / evaluation)

Clarify productive licensing with IBM before any production use. This is a
functional test record, not an independent audit or compliance approval.

## Automated scope

### Focused NAMELIST/SDR retest

Set `-e mq_audit_scope=namelist_sdr` to run only the two object lifecycles and
the general input-safety tests. The report identifies the reduced scope; PASS
does not constitute complete approval.

The Linux test definition omits `NLTYPE`, because IBM documents that parameter
for z/OS only. The namelist remains a list; the earlier serialization-error
hypothesis is unproven. The SDR receives the required `XMITQ`. The test creates
a separately collision-checked `BGA.*.XQ` with `USAGE(XMITQ)` and PUT/GET
disabled, retains it until the test completes, and removes it last. It starts
no channel and produces no message traffic. Creating an SDR without `xmitq` is
rejected before DEFINE. Both corrections still require focused live evidence.

References:

- [IBM DEFINE NAMELIST](https://www.ibm.com/docs/en/ibm-mq/9.4.x?topic=reference-define-namelist-define-list-names)
- [IBM DEFINE CHANNEL](https://www.ibm.com/docs/en/ibm-mq/9.4.x?topic=reference-define-channel-define-new-channel)

`ansible/playbooks/mq-audit.yml` runs the existing reconciler over HTTPS with
CA validation and Vault credentials. Random collision-checked `BGA.*` names
isolate the checks from existing objects. No channels are started.

| Area | Checks |
| --- | --- |
| QLOCAL, QREMOTE, QALIAS, QMODEL, TOPIC, NAMELIST | Check creation, DEFINE, idempotence, check ALTER, incremental ALTER, attribute preservation, check DELETE, DELETE and absence verification |
| SDR, RCVR, SVRCONN, CLNTCONN, CLUSSDR, CLUSRCVR | Definition lifecycle only; no communication or cluster approval |
| Safeguards | Type conflicts, immutable TOPICSTR, deletion approval, SYSTEM names, wildcards, unknown attributes, invalid enums and duplicate identities |
| Evidence | UTC time, Git revision, expectations/results, structured commands and codes, cleanup and SHA-256 manifest |

Cluster definitions can fail because of required attributes that the reconciler
does not support. That is a documented FAIL, not a suppressed error.

## Run from the controller

Deploy the intended code first and inspect `git status --short`; document local
changes in the test context. The suite is not an Ansible check-mode playbook.

```bash
python3 -m unittest discover -s tests -v
ansible-playbook ansible/playbooks/mq-audit.yml \
  -i ansible/inventory.yml -i ansible/inventory.local.yml \
  -e @ansible/vars/mq-lab.local.yml \
  -e mq_audit_confirm_test_mutations=true \
  --ask-vault-pass
```

Approval permits targeted test-object creation, ALTER and DELETE on BERGENLAB
only. Files below `ansible/reports/mq-audit/BGA.*/` are ignored and written with
restrictive permissions: `evidence.json`, `Pruefbericht.md` and `SHA256SUMS`.
On FAIL, evidence is written before the playbook stops. After a lost connection,
SIGKILL or uncertain cleanup, inspect the prefix; do not blindly retry or use
FORCE. Never put credentials in reports or Git.

Channel deletion uses the `CHLTYPE` returned by DISPLAY to select the correct
`CHLTABLE` (`CLNTTBL` or `QMGRTBL`). Missing or unknown types fail safely before
DELETE so identically named channel namespaces remain unambiguous.

Reference: [IBM MQ 9.4 DELETE CHANNEL](https://www.ibm.com/docs/en/ibm-mq/9.4.x?topic=reference-delete-channel-delete-channel).
The previously used values `clntconn` and `qmgr` were incorrect. The observed
`MQWB0121E` response for `clntconn` demonstrates the error; the corrected values
are `clnttbl` and `qmgrtbl`. Live reverification remains outstanding.

The live run at source commit `424cbaf` still rejected channel deletion with
HTTP 400. The CHLTABLE correction is therefore **not live-confirmed**; passing
offline tests do not replace that evidence. HTTP-400 diagnostics expose only
recognized IBM `msgId` identifiers and filtered `message` fields from bounded
JSON responses. Known credentials are removed and apparently sensitive messages
are suppressed; headers, raw responses, `explanation` and `action` are omitted.
Messages may still contain operational object names. HTTP 401/403 responses
remain body-free. Diagnostics do not trigger an automatic retry or another MQ
mutation.

## Optional report email

Add `-e mq_audit_mail_to=recipient@example.org` to enable email. Without that
variable, no email is sent. The three evidence files are submitted before the
final assertion even on FAIL. This requires an already configured local MTA
with `/usr/sbin/sendmail`; the playbook neither installs a mail server nor
accepts SMTP credentials.

Override the sender and sendmail path with `mq_audit_mail_from` and
`mq_audit_sendmail_path`. The default sender is `ansible@localhost`. Use a
relay-approved sender for external delivery. Successful MTA submission does
not prove mailbox delivery. A sending error preserves the evidence files and
fails the playbook. Preflight failures without evidence files send no email.
Attachments can contain operational metadata; use authorized recipients only.

## Remaining single-QMgr validation

The first automated run verifies the implemented object management, not every
IBM MQ capability on a queue manager. The following remain separate work:

- PUT/GET/Browse, persistence, commit/rollback and non-empty queue deletion.
- Invalid-password authentication, negative TLS cases, CHLAUTH/OAM and roles.
- Local publish/subscribe and dynamic queues.
- Service/container restart, host reboot, backup/restore and actual Syslog
  delivery; these require an approved interruption window.
- Boundary values and the complete matrix of supported attributes.

Untested items remain NOT TESTED. This topology cannot prove two-QMgr routing,
HA or active clusters. Offline tests are explicitly not real IBM MQ
compatibility evidence. A final audit report requires the actual evidence files
and organizational reviewer approval.

