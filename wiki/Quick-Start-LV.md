# Ātrā sākšana — IBM MQSC (Latviešu)

> Ar Ansible palaidiet numurētu MQSC failu esošā IBM MQ rindu pārvaldniekā. DISPLAY QMGR tikai nolasa datus.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Sagatavošana

Instalējiet atkarības vadības datorā un komandas izpildiet projekta saknes mapē.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Savienojuma iestatījumi

Lokālajā inventory katram pārvaldniekam norādiet savu aliasu, hostu, kontu un faktisko nosaukumu. Windows izmanto WinRM/PSRP; konteineriem vajag runtime un nosaukumu. Paroles glabājiet Vault.

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

## 3. MQSC fails

Izvēlieties globāli neizmantotu C######## ID. Komandas tiek izpildītas faila secībā.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audits un validācija

Audit pārbauda platformu un īsto MQ versiju. Validate pārbauda sintaksi, bet ne objektu stāvokli vai piekļuves tiesības.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Izpilde pēc apstiprināšanas

Tikai pēc pārskatīšanas izmantojiet precīzo plāna SHA-256 un apstiprinājuma atsauci. Neizdomājiet hash; apply var mainīt objektus.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Vairāki mērķi un pārskati

Vairākiem pārvaldniekiem veidojiet manifest ar sakārtotiem mērķiem un kopīgu MQSC failu. Pārskati: ansible/reports/mqsc/. Kļūda var atstāt daļējas izmaiņas.

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
