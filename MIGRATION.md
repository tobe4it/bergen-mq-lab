# Migration provenance

The initial standalone snapshot was extracted from:

- repository: `tobe4it/bergen-platform`
- source branch: `main`
- source commit: `e1c2698b90e9fee6f856435284d68bcb744eb7ee`
- extraction date: `2026-10-15`

The original per-file history remains available in the source repository.
Runtime hosts, local inventories, Vault files, IBM images and collected IBM
client artifacts were deliberately excluded from the transfer.

The generic LXC lifecycle playbooks and `remote_syslog` role were copied into
this repository because the MQ deployment orchestration imports them directly.
They are maintained here only to keep the lab independently deployable.

