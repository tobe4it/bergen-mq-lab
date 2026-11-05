# Kiirjuhend — IBM MQSC (Eesti)

> Käivita Ansible abil nummerdatud MQSC-fail olemasolevas IBM MQ järjekorralduris. DISPLAY QMGR on ainult lugemiseks.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Ettevalmistus

Paigalda sõltuvused juhtarvutisse ja käivita käsud projekti juurkataloogist.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Ühenduse seadistamine

Muuda kohalikku inventory-faili: igal järjekorralduril peab olema eraldi alias, host, kasutaja ja tegelik nimi. Windowsis kasuta WinRM/PSRP-d; konteinerites määra runtime ja nimi. Paroolid hoia Vaultis.

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

## 3. MQSC-fail

Vali üle kogu keskkonna kasutamata C######## tunnus. Käsud täidetakse failijärjekorras.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit ja valideerimine

Audit kontrollib platvormi ja tegelikku MQ versiooni. Validate kontrollib süntaksit, kuid mitte objektide olekut ega õigusi.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Rakendamine pärast kinnitamist

Alles pärast ülevaatust kasuta plaani täpset SHA-256 räsi ja kinnituse viidet. Ära mõtle räsi välja; apply võib objekte muuta.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Mitu sihtkohta ja aruanded

Mitme sihtkoha jaoks loo järjestatud manifest ja ühine MQSC-fail. Aruanded on ansible/reports/mqsc/. Viga võib jätta osalised muudatused.

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
