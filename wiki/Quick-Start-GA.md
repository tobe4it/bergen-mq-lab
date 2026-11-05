# Tús tapa — IBM MQSC (Gaeilge)

> Rith comhad MQSC uimhrithe ar bhainisteoir scuaine IBM MQ atá ann cheana trí Ansible. Ní dhéanann DISPLAY QMGR ach sonraí a léamh.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Ullmhúchán

Suiteáil na spleáchais ar an ríomhaire rialaithe agus rith na horduithe ó fhréamh an tionscadail.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Sonraí ceangail

Cuir ailias, óstach, cuntas agus fíorainm ar leith do gach bainisteoir sa chomhad inventory áitiúil. Úsáid WinRM/PSRP do Windows; do choimeádáin sonraigh runtime agus ainm. Coinnigh pasfhocail in Vault.

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

## 3. Comhad MQSC

Roghnaigh aitheantas C######## nach bhfuil in úsáid in áit ar bith. Déantar na horduithe in ord an chomhaid.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Iniúchadh agus bailíochtú

Seiceálann audit an t-ardán agus an fíorleagan MQ. Seiceálann validate an chomhréir freisin, ach ní dheimhníonn sé ceadanna ná staid réad.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Cur i bhfeidhm le cead

Tar éis athbhreithnithe, úsáid an SHA-256 cruinn ón bplean agus tagairt cheadaithe. Ná cum hais; féadfaidh apply réada a athrú.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Spriocanna iolracha agus tuairiscí

Do roinnt bainisteoirí, cruthaigh manifest le spriocanna in ord agus comhad comhroinnte. Tuairiscí: ansible/reports/mqsc/. D'fhéadfadh athruithe páirteacha fanacht tar éis earráide.

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
