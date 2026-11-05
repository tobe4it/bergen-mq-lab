# Inicio rápido — IBM MQSC (Español)

> Ejecute un archivo MQSC numerado en un gestor de colas IBM MQ existente mediante Ansible. DISPLAY QMGR es de solo lectura.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Preparación

Instale las dependencias en el controlador y ejecute los comandos desde la raíz del proyecto.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Conexión al gestor de colas

Edite el inventario local: cada gestor necesita alias, host, cuenta y nombre real propios. Windows usa WinRM/PSRP; los contenedores requieren motor y nombre. Guarde contraseñas en Vault.

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

## 3. Archivo MQSC

Elija un ID C######## único y sin usar. Los comandos se ejecutan en orden.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Auditoría y validación

Audit comprueba la plataforma y la versión real de MQ. Validate también comprueba la sintaxis, no los objetos ni las autorizaciones.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Aplicar con aprobación

Tras revisar el plan, utilice su SHA-256 exacto y una referencia de aprobación. No invente el hash; apply puede modificar objetos.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Varios destinos e informes

Para varios gestores use un manifiesto con destinos ordenados y un archivo común. Los informes están en ansible/reports/mqsc/. Los errores pueden producir cambios parciales.

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
