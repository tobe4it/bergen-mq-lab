# Bergen MQ Lab — Betriebs- und Referenzhandbuch

> Dieses Handbuch dokumentiert das Evaluierungslabor sowie die davon unabhängige MQSC-Deployment-Funktion. Das Labor ist nicht für den Produktivbetrieb freigegeben. Der MQSC-Adapter arbeitet mit bestehenden hostnativen IBM-MQ-Installationen und ersetzt weder Change-Freigaben noch Plattformtests.

## Contents

1. Überblick und Geltungsbereich
2. Architektur
3. Voraussetzungen
4. Installation
5. Konfiguration
6. MQSC-Deployment
7. Deklarative Objektverwaltung
8. TLS, LDAP und Berechtigungen
9. Audit und Tests
10. Betrieb und Fehleranalyse
11. Backup, Wiederherstellung und Rücknahme
12. Sicherheit, Freigaben und Grenzen

## 1. Überblick und Geltungsbereich

Das Labor stellt zwei getrennte IBM-MQ-Test-Queue-Manager und einen Java-Client mit Ansible, Proxmox-LXC, Rocky Linux und Podman/Quadlet bereit. Der eigenständige MQSC-Adapter arbeitet auf vorhandenen GNU/Linux-, AIX- oder Windows-Hosts, ohne MQ zu installieren. Der eingeschränkte REST-Abgleich ist nicht mit beliebiger MQSC-Ausführung gleichzusetzen.

Die README dient als Einstieg. Verbindliche technische Details stehen in `docs/MQ-LAB.md`, `docs/MQ.md`, `docs/MQ-TOPOLOGY.md` und `docs/MQSC-DEPLOY.md`.

## 2. Architektur

Der Controller verwaltet Proxmox-Gäste über SSH und Ansible. Die MQ-Container speichern persistente Daten außerhalb des Containers und bieten eine authentifizierte HTTPS-Verwaltungsschnittstelle. Der zweite Queue Manager und der Java-Client bilden getrennte Testeinheiten; Firewall-Regeln müssen zusätzlich geprüft werden.

Der eigenständige MQSC-Ablauf nutzt SSH auf GNU/Linux/AIX bzw. WinRM/PSRP auf Windows, legt MQSC-Dateien auf dem Ziel ab und startet das zur MQ-Installation gehörende `runmqsc`.

## 3. Voraussetzungen

Für die Laborinstallation werden ein Proxmox-Host, Rocky-Linux-9-LXC-Vorlage, Podman/Quadlet, Ansible und die Collections aus `requirements.yml` benötigt. Erforderlich sind standortspezifische Inventare, geprüfte SSH-Hostschlüssel, passende Netzwerkfreigaben und die IBM-Evaluierungsberechtigung.

Für MQSC sind eine bestehende IBM-MQ-Installation, das zugehörige `runmqsc`, der Betriebssystemzugang und eine berechtigte MQ-Identität erforderlich. Eine Developer-Lizenz berechtigt nicht automatisch zum Produktiveinsatz.

## 4. Installation

Beispielvariablen in ignorierte lokale Dateien kopieren, jeden Standortwert prüfen und Kennwörter im Ansible Vault hinterlegen. Evaluierungs- und Lizenzschalter erst nach Prüfung der Bedingungen aktivieren. Für die Erstinstallation `ansible/playbooks/deploy-mq-lab.yml`, für spätere Konfigurationsabgleiche `bootstrap-mq-lab.yml` verwenden.

Keine Erstinstallation gegen unbekannte Gäste oder Adressen wiederholen. VMID-Eindeutigkeit, Identität, Persistenz und Inventar prüfen. Der MQSC-Adapter installiert niemals IBM MQ.

## 5. Konfiguration

Adressen, VMIDs, TLS-Endpunkte, Queue-Manager-Namen und Zugangsdaten bleiben außerhalb von Git. Vorlagen liegen unter `ansible/examples/`, `ansible/vars/` und `ansible/group_vars/`. Vor jedem Lauf die ausgewählte Zieldefinition kontrollieren.

Für MQSC `mqsc_platform`, `mqsc_qmgr`, bei abweichendem Installationspfad `mqsc_runmqsc`, `mqsc_source` und eine eindeutige `mqsc_change_id` setzen. Je Ausführung genau einen Zielhost auswählen.

## 6. MQSC-Deployment

Das Playbook `ansible/playbooks/mqsc-deploy.yml` zuerst mit `mqsc_mode=audit`, anschließend mit `mqsc_mode=validate` und nach Freigabe mit `mqsc_mode=apply -e mqsc_confirm_apply=true` starten. Dateien können DEFINE, DELETE, ALTER und weitere gültige MQSC-Befehle in vorgegebener Reihenfolge enthalten.

`audit` prüft nur das Programm; `validate` prüft mit `runmqsc -v` die Syntax, nicht Objekte oder Berechtigungen. MQSC ist nicht transaktional. Teiländerungen und Protokolle prüfen; automatische Rücknahme, Doppel-Ausführungssperre und Queue-Manager-Lock fehlen. Windows-Staging-ACLs müssen standortspezifisch eingeschränkt werden.

## 7. Deklarative Objektverwaltung

Das Modul `ansible/library/mq_objects.py` gleicht einen begrenzten Satz von Queue-, Channel-, Topic- und Namelist-Attributen per HTTPS mit dem Istzustand ab. Nicht deklarierte Objekte werden nicht automatisch gelöscht. Check Mode und Diff gelten nur für diesen abgegrenzten Funktionsumfang.

Vor Änderungen `ansible/playbooks/mq-objects.yml --check --diff` mit geprüften lokalen und Vault-Variablen ausführen. CHLAUTH/OAM, Queue-Manager-Lebenszyklus und beliebige MQSC-Befehle deckt dieses Modul nicht ab.

## 8. TLS, LDAP und Berechtigungen

Zertifikatsprüfung für REST und MQ-Transport beibehalten. Das Labor verwendet eine private Test-CA mit eigenem Serverzertifikat und geschützten Schlüsseln. Zertifikate und private Schlüssel nicht einchecken. Client-Vertrauen, CHLAUTH, CONNAUTH, LDAP und OAM getrennt bewerten.

Weder Hostnamenprüfung deaktivieren noch Firewall-Netze unnötig erweitern oder pauschal `mqm` vergeben, um Tests bestehen zu lassen. Negativtests im isolierten Labor durchführen und produktive Sicherheitsrichtlinien nicht durch Evaluierungsautomatik überschreiben.

## 9. Audit und Tests

`python3 -m unittest discover -s tests -v` und Ansible-Syntaxprüfungen ausführen. Der Single-QMgr-Audit erfordert ausdrückliche Mutationsfreigaben und schreibt nachvollziehbare Ergebnisse mit SHA-256. Topologieprüfungen sind separat abzunehmen.

Offline- und Mock-Tests beweisen keine IBM-MQ-Kompatibilität. Nicht ausgeführte Live-Tests als NOT TESTED kennzeichnen. Betriebssystem, MQ-Version, Git-Revision, Ergebnis und Nachweise protokollieren.

## 10. Betrieb und Fehleranalyse

Fehler der Reihe nach bei Controller-Verbindung, Betriebssystem-Identität, Queue-Manager-Status, Installationsauswahl, Zertifikatskette, MQ-Rechten und Logs eingrenzen. Im Labor `journalctl -u bergen-mq-lab.service` und die MQ-Fehlerprotokolle prüfen.

Bei REST HTTP 401/403 Identität, CA und CSRF-Header prüfen statt Kontrollen abzuschalten. Bei MQSC-Fehlern die geschützten JSON-Berichte unter `ansible/reports/mqsc/` lesen; teilweise ausgeführte Änderungen niemals blind wiederholen.

## 11. Backup, Wiederherstellung und Rücknahme

Persistente MQ-Daten, Konfiguration, Zertifikate und externe Backups gemäß Standortregel sichern. Eine Container-Neuerstellung entfernt nicht zwangsläufig Daten, ist aber kein Backup. Vor destruktiven Änderungen einen geprüften Wiederherstellungspunkt schaffen.

MQSC besitzt keine übergreifende Transaktion und kein automatisches Rollback. Gegenänderungen im Voraus prüfen und vor einem Wiederanlauf den Istzustand kontrollieren. Restore-Test, Host-Neustart und Wiederanlaufziele separat erproben.

## 12. Sicherheit, Freigaben und Grenzen

Alle Laborbeispiele sind ausschließlich für Evaluation vorgesehen. Produktivbetrieb erfordert getrennte IBM-Lizenz-, Sicherheits-, Change- und Kompatibilitätsfreigaben. Vault-Daten, Berichte und MQSC-Staging geschützt aufbewahren. Änderungen mit Review, enger Zielauswahl und Change-ID durchführen.

Der derzeitige MQSC-Adapter unterstützt keine hostseitige Containerausführung, keine MQ-Versionen ohne benötigte `runmqsc`-Optionen, keine verteilten Sperren und keine garantierte Einmalausführung. Freigaben, Wartungsfenster, Backups und Plattformabnahme muss ein übergeordneter Prozess regeln.

---

Références techniques / Technische Referenzen: [README](https://github.com/tobe4it/bergen-mq-lab/blob/main/README.md) · [Lab](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-LAB.md) · [REST](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ.md) · [MQSC](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md) · [Audit](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-AUDIT.md) · [Topology](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-TOPOLOGY.md).
