# Snelstart — IBM MQSC (Nederlands)

> Voer met Ansible een genummerd MQSC-bestand uit op een bestaande IBM MQ-queue manager. DISPLAY QMGR leest alleen gegevens.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Voorbereiden

Installeer de afhankelijkheden op de controller. Werk vanuit de hoofdmap van het project.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Verbindingen configureren

Elke queue manager krijgt in de lokale inventory een eigen alias, host, account en werkelijke naam. Windows gebruikt WinRM/PSRP; containers hebben runtime en containernaam nodig. Bewaar wachtwoorden in Vault.

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

## 3. MQSC-bestand

Kies een wereldwijd ongebruikt C########-nummer. De opdrachten worden in bestandsvolgorde uitgevoerd.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit en validatie

Audit controleert platform en werkelijke MQ-versie. Validate controleert ook syntaxis, niet de objectstatus of rechten.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Uitvoeren na goedkeuring

Gebruik pas na beoordeling de exacte SHA-256 van het plan en een goedkeuringsreferentie. Verzin geen hash; apply kan objecten wijzigen.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Meerdere doelen en rapporten

Gebruik voor meerdere managers een manifest met geordende doelen en een gedeeld MQSC-bestand. Rapporten: ansible/reports/mqsc/. Fouten kunnen gedeeltelijke wijzigingen achterlaten.

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
