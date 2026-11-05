# Rychlý začátek — IBM MQSC (Čeština)

> Tento postup spustí očíslované příkazy MQSC na existujícím správci front IBM MQ pomocí Ansible. DISPLAY QMGR pouze čte stav.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Příprava

Nainstalujte závislosti na řídicím počítači. Příkazy spouštějte v kořenové složce projektu.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Připojení správce front

Upravte místní inventory: každému správci dejte zvláštní alias, adresu, účet a skutečný název. Windows vyžaduje WinRM/PSRP; kontejnery runtime a název. Hesla uložte do Vaultu.

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

## 3. Soubor MQSC

Zvolte nepoužité ID C########. Příkazy se vykonají v pořadí souboru.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit a ověření

Audit ověří platformu a skutečnou verzi MQ. Validate kontroluje syntaxi, nikoli existenci objektů či oprávnění.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Spuštění po schválení

Po kontrole plánu použijte jeho přesný SHA-256 a identifikátor schválení. Hash nevymýšlejte; apply může měnit objekty.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Více cílů a výsledky

Pro více správců použijte manifest s uspořádanými cíli a společný soubor MQSC. Výsledky jsou v ansible/reports/mqsc/. Při chybě mohly vzniknout dílčí změny.

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
