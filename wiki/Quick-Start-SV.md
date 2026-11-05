# Snabbstart — IBM MQSC (Svenska)

> Kör en numrerad MQSC-fil mot en befintlig IBM MQ-köhanterare med Ansible. DISPLAY QMGR läser bara uppgifter.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Förberedelser

Installera beroenden på styrdatorn och arbeta från projektets rotmapp.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Anslutningar

Ge varje köhanterare ett eget alias, värddator, konto och verkligt namn i lokal inventory. Windows använder WinRM/PSRP; containrar kräver runtime och namn. Lagra lösenord i Vault.

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

Välj ett globalt oanvänt C########-ID. Kommandona körs i filordning.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit och validering

Audit kontrollerar plattform och faktisk MQ-version. Validate kontrollerar också syntax, men inte objektstatus eller behörighet.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Kör efter godkännande

Använd först efter granskning planens exakta SHA-256 och en godkännandereferens. Hitta inte på någon hash; apply kan ändra objekt.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Flera mål och rapporter

För flera köhanterare används ett manifest med ordnade mål och en gemensam MQSC-fil. Rapporter: ansible/reports/mqsc/. Fel kan lämna delvisa ändringar.

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
