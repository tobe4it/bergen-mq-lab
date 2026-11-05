# Brzi početak — IBM MQSC (Hrvatski)

> Pokrenite numeriranu MQSC datoteku na postojećem IBM MQ upravitelju redova pomoću Ansiblea. DISPLAY QMGR samo čita podatke.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Priprema

Instalirajte ovisnosti na kontroleru i pokrenite naredbe iz korijena projekta.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Postavke veze

U lokalnom inventoryju svakom upravitelju dodijelite alias, host, račun i stvarno ime. Za Windows koristite WinRM/PSRP; kontejneri trebaju runtime i naziv. Lozinke čuvajte u Vaultu.

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

## 3. MQSC datoteka

Odaberite globalno neiskorištenu oznaku C########. Naredbe se izvode redom iz datoteke.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit i provjera

Audit provjerava platformu i stvarnu verziju MQ-a. Validate dodatno provjerava sintaksu, ali ne stanje objekata ni ovlasti.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Izvršavanje uz odobrenje

Nakon pregleda koristite točan SHA-256 plana i referencu odobrenja. Nemojte izmišljati hash; apply može mijenjati objekte.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Više ciljeva i izvještaji

Za više upravitelja stvorite manifest s uređenim ciljevima i zajedničkom MQSC datotekom. Izvještaji su u ansible/reports/mqsc/. Pogreška može ostaviti djelomične promjene.

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
