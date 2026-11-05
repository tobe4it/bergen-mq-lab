# Gyors kezdés — IBM MQSC (Magyar)

> Számozott MQSC-fájlt futtathat meglévő IBM MQ sorkezelőn Ansible segítségével. A DISPLAY QMGR csak olvas.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Előkészítés

Telepítse a függőségeket a vezérlőre, és a projekt gyökérkönyvtárából dolgozzon.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Kapcsolatok beállítása

A helyi inventory minden sorkezelőhöz külön aliast, hostot, felhasználót és valódi nevet tartalmazzon. Windowson WinRM/PSRP; konténereknél runtime és név szükséges. Jelszavak: Vault.

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

## 3. MQSC-fájl

Válasszon globálisan még nem használt C######## azonosítót. A parancsok a fájlbeli sorrendben futnak.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit és ellenőrzés

Az audit ellenőrzi a platformot és a tényleges MQ-verziót. A validate a szintaxist is ellenőrzi, az objektumállapotot és a jogosultságokat nem.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Végrehajtás jóváhagyással

Ellenőrzés után használja a terv pontos SHA-256 értékét és jóváhagyási hivatkozását. Ne találjon ki hash-t; az apply módosíthat objektumokat.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Több cél és jelentések

Több sorkezelőhöz hozzon létre rendezett céllistájú manifestet és közös MQSC-fájlt. Jelentések: ansible/reports/mqsc/. Hiba részleges módosítást hagyhat.

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
