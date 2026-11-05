# Hitri začetek — IBM MQSC (Slovenščina)

> Z Ansible izvedite oštevilčeno datoteko MQSC na obstoječem upravljalniku vrst IBM MQ. DISPLAY QMGR samo bere podatke.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Priprava

Namestite odvisnosti na nadzorni računalnik in delajte iz korenske mape.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Nastavitev povezav

V lokalnem inventory ima vsak upravljalnik svoj vzdevek, gostitelja, račun in dejansko ime. Windows uporablja WinRM/PSRP; vsebniki potrebujejo runtime in ime. Gesla hranite v Vaultu.

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

## 3. Datoteka MQSC

Izberite globalno še neuporabljen C######## ID. Ukazi se izvajajo v vrstnem redu datoteke.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit in preverjanje

Audit preveri platformo in dejansko različico MQ. Validate preveri tudi skladnjo, ne pa stanja objektov ali pravic.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Izvedba po odobritvi

Po pregledu uporabite natančni SHA-256 načrta in referenco odobritve. Hasha si ne izmišljajte; apply lahko spremeni objekte.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Več ciljev in poročila

Za več upravljalnikov pripravite manifest z urejenimi cilji in skupno datoteko MQSC. Poročila: ansible/reports/mqsc/. Napake lahko pustijo delne spremembe.

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
