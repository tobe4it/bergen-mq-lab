# IBM MQ lab: isolated transport PKI (historical PR #42)

The Bergen MQ evaluation lab uses separate CA/key material for each queue
manager, preserving the existing `bergenlab` identity. This is a **lab
capability only**, not production TLS authorization.

Two deliberately distinct playbooks:

* `ansible/playbooks/mq-transport-pki-prepare.yml`: requires
  `mq_transport_pki_prepare=true` and is **not check-mode compatible**.
  It generates protected keys on the selected MQ lab guests and exchanges
  **only public peer CA certificates**; no service restart.
* `ansible/playbooks/mq-transport-pki-activate.yml`: requires BOTH
  `mq_transport_pki_activate=true` and
  `mq_transport_restart_approved=true`. It can alter the existing
  Quadlet and **restart the lab container**. Never run without a
  maintenance-window approval, current backup and verified rollback.

The two opt-in read-only Quadlet mounts are off by default. This Git merge
does not run either playbook or copy any key. Use site-local, ignored
inventory and Vault variables. Do not commit internal addresses, private
keys, certificates or log output.

Release gates still open: controller-side tests and syntax, read-only
comparison of live Quadlet to the intended base, positive/negative TLS
handshakes on MQ 9.4, CHLAUTH/OAM and original-identity rollback. Those
are **not established by offline CI**.
