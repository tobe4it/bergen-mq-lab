# Ephemeral mTLS transport audit (extracted from bergen-platform #42)

Development fixtures for the IBM MQ 9.4 evaluation lab only. The
`mq-topology-audit.yml` runner keeps transient SDR/RCVR and XMITQ changes
**off by default** (`mq_topology_transient_transport=false`), and requires
additional explicit evidence flags when opted in. This is not a standalone
permission to run against real queue managers.

The one-shot namespace uses bounded `AUDIT.<7-HEX>` objects; sender/receiver
channels use a dedicated `bergentransport` CERTLABL and TLS 1.3 CipherSpec.
No CHLAUTH/OAM grants or static long-lived channels are installed here.
Unknown channel state, nonempty XMITQ or incomplete cleanup can leave
residual objects; operators MUST triage before another run and MUST NOT use
FORCE, PURGE or delete production objects.

**Prerequisites**: separate PKI Draft #1, verified authenticated REST/MQSC
permissions, independent certificate peer trust, source-restricted firewall
and recorded negative tests. Check the live installed MQ version, IBM MQ
REST command support and review all actual object names before approving
a mutation. The production-of-lab objects and backups must be preserved.

No controller secrets, MAC/IP records, credentials or deployment approvals
are stored in this repository. Offline tests use RFC 5737 TEST-NET addresses;
they do not prove real cross-QMgr mTLS.
