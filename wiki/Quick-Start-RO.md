# Pornire rapidă — IBM MQSC (Română)

> Rulați cu Ansible un fișier MQSC numerotat pe un manager de cozi IBM MQ existent. DISPLAY QMGR doar citește date.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Pregătire

Instalați dependențele pe controler și rulați comenzile din rădăcina proiectului.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Configurarea conexiunilor

În inventory-ul local, fiecare manager are alias, host, cont și nume real distincte. Windows folosește WinRM/PSRP; containerele necesită runtime și nume. Păstrați parolele în Vault.

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

## 3. Fișier MQSC

Alegeți un ID C######## neutilizat global. Comenzile se execută în ordinea din fișier.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit și validare

Audit verifică platforma și versiunea MQ reală. Validate verifică sintaxa, dar nu starea obiectelor sau drepturile.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Aplicare cu aprobare

După verificare folosiți SHA-256 exact al planului și o referință de aprobare. Nu inventați hash; apply poate modifica obiecte.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Ținte multiple și rapoarte

Pentru mai mulți manageri creați un manifest cu ținte ordonate și fișier MQSC comun. Rapoarte: ansible/reports/mqsc/. Erorile pot lăsa modificări parțiale.

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
