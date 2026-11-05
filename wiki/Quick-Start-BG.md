# Бърз старт — IBM MQSC (Български)

> Използвайте Ansible за изпълнение на номерирани MQSC команди в съществуващ IBM MQ. Примерът DISPLAY QMGR само чете данни.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Подготовка

Инсталирайте зависимостите на контролера. Изпълнявайте командите от основната директория.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Връзки към queue manager

Редактирайте локалния inventory: задайте отделен alias, адрес, потребител и име на queue manager. За Windows използвайте WinRM/PSRP, за контейнер — runtime и име. Паролите съхранявайте във Vault.

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

## 3. MQSC файл

Изберете неизползвано ID C########. Командите се изпълняват в реда на файла.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit и проверка

Audit проверява платформата и реалната MQ версия. Validate проверява синтаксиса, но не гарантира наличието на обекти или права.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Изпълнение с одобрение

След преглед използвайте точния SHA-256 на плана и референция за одобрение. Не измисляйте хеш; apply може да променя обекти.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Множество цели и отчети

При повече queue managers използвайте manifest с подредени цели и общ MQSC файл. Отчетите са в ansible/reports/mqsc/. При грешка са възможни частични промени.

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
