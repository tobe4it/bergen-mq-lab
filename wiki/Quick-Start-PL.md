# Szybki start — IBM MQSC (Polski)

> Uruchom numerowany plik MQSC na istniejącym menedżerze kolejek IBM MQ za pomocą Ansible. DISPLAY QMGR tylko odczytuje dane.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Przygotowanie

Zainstaluj zależności na kontrolerze i uruchamiaj polecenia z katalogu głównego.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Konfiguracja połączeń

W lokalnym inventory nadaj każdemu menedżerowi osobny alias, host, konto i rzeczywistą nazwę. Windows używa WinRM/PSRP; kontenery wymagają runtime i nazwy. Hasła przechowuj w Vault.

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

## 3. Plik MQSC

Wybierz globalnie nieużywany numer C########. Polecenia wykonają się w kolejności z pliku.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audyt i walidacja

Audit sprawdza platformę i rzeczywistą wersję MQ. Validate sprawdza składnię, lecz nie stan obiektów ani uprawnienia.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Wykonanie po zatwierdzeniu

Dopiero po przeglądzie użyj dokładnego SHA-256 planu i referencji zatwierdzenia. Nie wymyślaj hasha; apply może zmienić obiekty.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Wiele celów i raporty

Dla wielu menedżerów utwórz manifest z uporządkowanymi celami i wspólnym plikiem MQSC. Raporty: ansible/reports/mqsc/. Błąd może pozostawić częściowe zmiany.

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
