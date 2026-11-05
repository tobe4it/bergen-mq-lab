# Démarrage rapide — IBM MQSC (Français)

> Exécutez un fichier MQSC numéroté sur un gestionnaire de files IBM MQ existant avec Ansible. DISPLAY QMGR est en lecture seule.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Préparer le contrôleur

Installez les dépendances sur le contrôleur et exécutez les commandes à la racine du dépôt.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Configurer les connexions MQ

Modifiez l'inventaire local : chaque gestionnaire possède un alias, un hôte, un compte et son nom réel. Windows utilise WinRM/PSRP ; les conteneurs nécessitent un moteur et un nom. Conservez les secrets dans Vault.

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

## 3. Créer le fichier MQSC

Choisissez un identifiant C######## unique et inutilisé. Les commandes s'exécutent dans l'ordre du fichier.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Audit et validation

Audit contrôle la plateforme et la version réelle de MQ. Validate contrôle aussi la syntaxe, sans garantir l'état des objets ni les autorisations.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Appliquer après approbation

Après examen du plan, fournissez son SHA-256 exact et une référence d'approbation. N'inventez pas d'empreinte ; apply peut modifier les objets.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Plusieurs cibles et rapports

Pour plusieurs gestionnaires, préparez un manifeste de cibles ordonnées et un fichier commun. Rapports : ansible/reports/mqsc/. Une erreur peut laisser des modifications partielles.

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
