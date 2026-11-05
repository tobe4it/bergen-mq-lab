# Hurtig start — IBM MQSC (Dansk)

> Denne guide udfører en nummereret MQSC-fil på en eksisterende IBM MQ-kømanager via Ansible. DISPLAY QMGR læser kun data.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Forberedelse

Installer afhængigheder på Ansible-controlleren. Kør kommandoerne fra projektets rodmappe.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Forbindelse til kømanager

Rediger det lokale inventory med særskilt alias, adresse, konto og faktisk navn for hver kømanager. Windows kræver WinRM/PSRP; containere kræver runtime og navn. Opbevar adgangskoder i Vault.

```yaml
mqsc_targets:
  hosts:
    linux-mq:
      ansible_host: mq.example.invalid
      ansible_user: mqdeploy
      mqsc_platform: linux
      mqsc_qmgr: QM01
      mqsc_installation: /opt/mqm
      mqsc_become: true
      mqsc_become_user: mqm
```

## 3. MQSC-fil

Vælg et ubrugt C########-nummer. Kommandoerne udføres i filrækkefølge.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit og validering

Audit kontrollerer platform og faktisk MQ-version. Validate kontrollerer syntaksen, men ikke objektstatus eller rettigheder.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Udfør efter godkendelse

Brug kun den præcise SHA-256 fra den gennemgåede plan og en godkendelsesreference. Opfind ikke en hash; apply kan ændre objekter.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Flere mål og rapporter

Brug et manifest med ordnede mål og en fælles MQSC-fil til flere kømanagere. Rapporter ligger i ansible/reports/mqsc/. Fejl kan efterlade delvise ændringer.

```yaml
# mqsc/changes/C00000011.yml
targets: [linux-mq, aix-mq]
mq_series: ['9.4', '10.0']
```

```bash
printf 'DISPLAY QMGR\n' > mqsc/changes/C00000011.mqsc
python3 tools/mqsc_change.py C00000011 -i ansible/inventory.mqsc.local.yml --mode validate
```

[Technical reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)
