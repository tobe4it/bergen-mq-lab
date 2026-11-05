# Greitoji pradžia — IBM MQSC (Lietuvių)

> Naudodami Ansible paleiskite sunumeruotą MQSC failą esamame IBM MQ eilių tvarkytuve. DISPLAY QMGR tik skaito duomenis.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Paruošimas

Įdiekite priklausomybes valdymo kompiuteryje ir dirbkite projekto šakniniame kataloge.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Ryšio nustatymai

Vietiniame inventory kiekvienam tvarkytuvui nurodykite atskirą aliasą, hostą, paskyrą ir tikrąjį vardą. Windows naudokite WinRM/PSRP; konteineriams nurodykite runtime ir vardą. Slaptažodžius saugokite Vault.

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

## 3. MQSC failas

Pasirinkite globaliai nenaudotą C######## ID. Komandos vykdomos failo eilės tvarka.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Auditas ir tikrinimas

Audit patikrina platformą ir tikrąją MQ versiją. Validate tikrina ir sintaksę, bet ne objektų būseną ar teises.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Taikymas gavus patvirtinimą

Tik po peržiūros nurodykite tikslų plano SHA-256 ir patvirtinimo nuorodą. Nesugalvokite hash; apply gali keisti objektus.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Kelios sistemos ir ataskaitos

Keliems tvarkytuvams sukurkite manifest su surikiuotais tikslais ir bendru MQSC failu. Ataskaitos: ansible/reports/mqsc/. Klaida gali palikti dalinius pakeitimus.

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
