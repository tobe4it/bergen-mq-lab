# Início rápido — IBM MQSC (Português)

> Execute com Ansible um ficheiro MQSC numerado num gestor de filas IBM MQ existente. DISPLAY QMGR apenas lê dados.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Preparação

Instale as dependências no controlador e trabalhe na raiz do projeto.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Configurar ligações

No inventário local, cada gestor precisa de um alias, anfitrião, conta e nome real próprios. Windows usa WinRM/PSRP; contentores exigem runtime e nome. Guarde palavras-passe no Vault.

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

## 3. Ficheiro MQSC

Escolha um identificador C######## não utilizado globalmente. Os comandos seguem a ordem do ficheiro.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Auditoria e validação

Audit verifica a plataforma e a versão real de MQ. Validate verifica também a sintaxe, não o estado dos objetos ou as permissões.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Executar após aprovação

Após revisão utilize o SHA-256 exato do plano e a referência de aprovação. Não invente um hash; apply pode alterar objetos.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Vários destinos e relatórios

Para vários gestores crie um manifesto com destinos ordenados e ficheiro comum. Relatórios: ansible/reports/mqsc/. Um erro pode deixar alterações parciais.

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
