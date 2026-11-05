# Schnellstart — IBM MQSC (Deutsch)

> Diese Anleitung führt eine nummerierte MQSC-Datei über Ansible auf einem vorhandenen IBM-MQ-Queue-Manager aus. DISPLAY QMGR liest nur Informationen.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Controller vorbereiten

Installiere die Controller-Abhängigkeiten. Führe die Befehle im Stammverzeichnis des Repositorys aus.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Verbindungsdaten konfigurieren

Bearbeite das lokale Inventory: Für jeden Queue Manager werden eigener Alias, Host, Benutzer und tatsächlicher QMGR-Name benötigt. Windows verwendet WinRM/PSRP, Container benötigen Runtime und Containername. Geheimnisse gehören in Vault.

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

## 3. MQSC-Datei anlegen

Wähle eine global unbenutzte C########-ID. Die MQSC-Befehle werden in Dateireihenfolge ausgeführt.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit und Syntaxprüfung

Audit prüft Plattform und tatsächliche MQ-Version. Validate prüft zusätzlich die Syntax, jedoch weder Objektzustand noch ausreichende Berechtigungen.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Mit Freigabe ausführen

Verwende erst nach Prüfung den tatsächlichen SHA-256 des Plans und die Change-Freigabereferenz. Keine erfundene Prüfsumme einsetzen; apply kann Änderungen auslösen.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Mehrere Queue Manager und Ergebnisse

Für mehrere Queue Manager ein Manifest mit geordneter Zielliste und gemeinsamer MQSC-Datei verwenden. Ergebnisse stehen unter ansible/reports/mqsc/. Bei Fehlern können Teiländerungen bestehen.

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
