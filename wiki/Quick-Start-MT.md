# Bidu ta' malajr — IBM MQSC (Malti)

> Uża Ansible biex tħaddem fajl MQSC numerat fuq queue manager IBM MQ eżistenti. DISPLAY QMGR jaqra biss id-data.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Tħejjija

Installa d-dipendenzi fuq il-kontrollur u ħaddem il-kmandi mill-folder ewlieni tal-proġett.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Dettalji tal-konnessjoni

Fl-inventory lokali agħti lil kull queue manager alias, host, kont u isem veru separati. Windows juża WinRM/PSRP; containers jeħtieġu runtime u isem. Żomm passwords f'Vault.

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

## 3. Fajl MQSC

Agħżel ID C######## mhux użat. Il-kmandi jsiru fl-ordni tal-fajl.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit u verifika

Audit jiċċekkja l-pjattaforma u l-verżjoni reali ta' MQ. Validate jiċċekkja wkoll is-sintassi, mhux l-istat tal-oġġetti jew il-permessi.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Applika bl-approvazzjoni

Wara reviżjoni, uża SHA-256 eżatt tal-pjan u referenza tal-approvazzjoni. Tivvintax hash; apply jista' jibdel l-oġġetti.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Diversi miri u rapporti

Għal diversi queue managers ħejji manifest b'miri fl-ordni u fajl komuni. Rapporti: ansible/reports/mqsc/. Żball jista' jħalli bidliet parzjali.

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
