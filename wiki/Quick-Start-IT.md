# Avvio rapido — IBM MQSC (Italiano)

> Eseguire con Ansible un file MQSC numerato su un queue manager IBM MQ esistente. DISPLAY QMGR è di sola lettura.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Preparazione

Installare le dipendenze sul controller ed eseguire i comandi dalla radice del progetto.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Configurare le connessioni

Nell'inventario locale ogni queue manager deve avere alias, host, account e nome reale distinti. Windows usa WinRM/PSRP; i container richiedono runtime e nome. Conservare le password in Vault.

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

## 3. File MQSC

Scegliere un ID C######## mai utilizzato globalmente. I comandi vengono eseguiti nell'ordine del file.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit e verifica

Audit verifica piattaforma e versione MQ effettiva. Validate controlla anche la sintassi, non lo stato degli oggetti o le autorizzazioni.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Applicare con approvazione

Dopo la revisione usare l'esatto SHA-256 del piano e un riferimento di approvazione. Non inventare hash; apply può modificare gli oggetti.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Più destinazioni e report

Per più queue manager creare un manifest con destinazioni ordinate e file condiviso. Report: ansible/reports/mqsc/. Errori possono lasciare modifiche parziali.

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
