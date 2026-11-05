# Γρήγορη εκκίνηση — IBM MQSC (Ελληνικά)

> Ο οδηγός εκτελεί αριθμημένες εντολές MQSC σε υπάρχοντα διαχειριστή ουρών IBM MQ με το Ansible. Το DISPLAY QMGR είναι μόνο για ανάγνωση.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Προετοιμασία

Εγκαταστήστε τις εξαρτήσεις στον ελεγκτή Ansible. Εκτελέστε τις εντολές από τον αρχικό κατάλογο του έργου.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Στοιχεία σύνδεσης

Στο τοπικό inventory ορίστε διαφορετικό ψευδώνυμο, διεύθυνση, χρήστη και πραγματικό όνομα για κάθε διαχειριστή. Για Windows χρησιμοποιήστε WinRM/PSRP· για containers ορίστε runtime και όνομα. Αποθηκεύστε κωδικούς στο Vault.

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

## 3. Αρχείο MQSC

Επιλέξτε αχρησιμοποίητο αναγνωριστικό C########. Οι εντολές εκτελούνται με τη σειρά του αρχείου.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Έλεγχος και επαλήθευση

Η audit ελέγχει την πλατφόρμα και την πραγματική έκδοση MQ. Η validate ελέγχει τη σύνταξη, όχι την ύπαρξη αντικειμένων ή τα δικαιώματα.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Εκτέλεση με έγκριση

Μετά την έγκριση χρησιμοποιήστε το ακριβές SHA-256 του σχεδίου και την αναφορά έγκρισης. Μην επινοείτε hash· η apply μπορεί να κάνει αλλαγές.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Πολλαπλοί στόχοι και αναφορές

Για πολλούς διαχειριστές δημιουργήστε manifest με ταξινομημένους στόχους και κοινό MQSC. Αναφορές: ansible/reports/mqsc/. Μια αποτυχία μπορεί να αφήσει μερικές αλλαγές.

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
