# Rýchly štart — IBM MQSC (Slovenčina)

> Spustite pomocou Ansible očíslovaný súbor MQSC na existujúcom správcovi frontov IBM MQ. DISPLAY QMGR iba číta údaje.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Príprava

Nainštalujte závislosti na riadiacom počítači a pracujte z koreňového priečinka projektu.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Nastavenie pripojení

V miestnom inventory každý správca potrebuje vlastný alias, hostiteľa, účet a skutočný názov. Windows používa WinRM/PSRP; kontajnery potrebujú runtime a názov. Heslá ukladajte do Vaultu.

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

## 3. Súbor MQSC

Zvoľte globálne nepoužité číslo C########. Príkazy sa vykonajú v poradí súboru.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit a validácia

Audit overí platformu a skutočnú verziu MQ. Validate overí aj syntax, nie stav objektov alebo oprávnenia.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Spustenie po schválení

Po kontrole použite presný SHA-256 plánu a referenciu schválenia. Hash si nevymýšľajte; apply môže meniť objekty.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Viac cieľov a správy

Pre viac správcov vytvorte manifest s usporiadanými cieľmi a spoločným súborom MQSC. Správy: ansible/reports/mqsc/. Chyby môžu zanechať čiastočné zmeny.

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
