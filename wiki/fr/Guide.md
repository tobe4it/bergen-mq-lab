# Bergen MQ Lab — Guide d'exploitation et de référence

> Ce guide décrit le laboratoire d'évaluation et l'adaptateur MQSC autonome. Le laboratoire n'est pas homologué pour la production. L'adaptateur cible des installations IBM MQ natives existantes et ne remplace ni l'approbation du changement ni les essais de compatibilité.

## Contents

1. Présentation et périmètre
2. Architecture
3. Prérequis
4. Installation
5. Configuration
6. Déploiement MQSC
7. Administration déclarative des objets
8. TLS, LDAP et autorisations
9. Audits et tests
10. Exploitation et dépannage
11. Sauvegarde, restauration et retour arrière
12. Sécurité, gouvernance et limites

## 1. Présentation et périmètre

Le laboratoire déploie deux gestionnaires de files IBM MQ isolés et un client Java avec Ansible, Proxmox LXC, Rocky Linux et Podman/Quadlet. L'adaptateur MQSC autonome utilise des hôtes GNU/Linux, AIX ou Windows existants sans installer MQ. La réconciliation REST limitée ne constitue pas une exécution MQSC universelle.

Le fichier README sert de point de départ. Les références détaillées se trouvent dans `docs/MQ-LAB.md`, `docs/MQ.md`, `docs/MQ-TOPOLOGY.md` et `docs/MQSC-DEPLOY.md`.

## 2. Architecture

Le contrôleur orchestre les invités Proxmox via SSH et Ansible. Les conteneurs MQ conservent les données persistantes hors du conteneur et proposent une interface d'administration HTTPS authentifiée. Le deuxième gestionnaire et le client Java sont isolés ; les règles de pare-feu restent à examiner séparément.

L'adaptateur MQSC utilise SSH sous GNU/Linux/AIX ou WinRM/PSRP sous Windows, transfère un fichier MQSC sur la cible et exécute le programme `runmqsc` de l'installation sélectionnée.

## 3. Prérequis

Pour le laboratoire, prévoir un hôte Proxmox, un modèle LXC Rocky Linux 9, Podman/Quadlet, Ansible et les collections de `requirements.yml`. Préparer les inventaires locaux, les clés SSH vérifiées, les règles réseau et les droits d'évaluation IBM nécessaires.

Pour MQSC, disposer d'une installation IBM MQ existante, du programme `runmqsc` correspondant, d'un accès au système d'exploitation et d'un compte autorisé. Une licence développeur n'autorise pas automatiquement la production.

## 4. Installation

Copier les exemples de variables vers des fichiers locaux ignorés par Git, examiner tous les paramètres et placer les secrets dans Ansible Vault. N'activer les confirmations d'évaluation et de licence qu'après vérification des conditions. Utiliser `ansible/playbooks/deploy-mq-lab.yml` pour le premier déploiement et `bootstrap-mq-lab.yml` pour les ajustements suivants.

Ne pas relancer le premier déploiement sur un invité inconnu. Vérifier l'unicité du VMID, l'identité, la persistance et les inventaires. L'adaptateur MQSC n'installe jamais IBM MQ.

## 5. Configuration

Conserver les adresses, VMID, points TLS, noms des gestionnaires et identifiants hors de Git. Les exemples se trouvent dans `ansible/examples/`, `ansible/vars/` et `ansible/group_vars/`. Contrôler la cible avant chaque opération.

Pour MQSC, définir `mqsc_platform`, `mqsc_qmgr`, si nécessaire `mqsc_runmqsc`, puis `mqsc_source` et un `mqsc_change_id` unique. Sélectionner exactement un hôte par exécution.

## 6. Déploiement MQSC

Exécuter `ansible/playbooks/mqsc-deploy.yml` avec `mqsc_mode=audit`, puis `mqsc_mode=validate`, puis seulement après validation avec `mqsc_mode=apply -e mqsc_confirm_apply=true`. Le fichier peut contenir DEFINE, DELETE, ALTER et d'autres commandes MQSC valides, exécutées dans leur ordre d'apparition.

`audit` vérifie uniquement l'exécutable ; `validate` utilise `runmqsc -v` pour contrôler la syntaxe, pas les objets ni les droits. MQSC n'est pas transactionnel. Examiner les changements partiels ; pas de rollback automatique, de registre anti-doublon ni de verrou de gestionnaire. Les ACL du répertoire Windows doivent être restreintes localement.

**Versions IBM MQ ciblées :** IBM MQ 9.2, 9.3, 9.4 et 10.0 (y compris MQ 10.0 LTS et 10.0.1 CD) font partie du périmètre architectural, sans constituer une preuve de compatibilité testée. Avant toute approbation, vérifier la version installée, la syntaxe MQSC, les autorisations et l'adaptateur d'exécution sur chaque système. Voir `docs/MQSC-DEPLOY.md`.

## 7. Administration déclarative des objets

Le module `ansible/library/mq_objects.py` compare un ensemble limité d'attributs des files, canaux, topics et namelists avec l'état réel via HTTPS. Les objets absents de la déclaration YAML ne sont pas supprimés. Le mode de vérification et le diff couvrent uniquement ce périmètre.

Avant une modification, utiliser `ansible/playbooks/mq-objects.yml --check --diff` avec des variables locales examinées et des secrets Vault. Ce module ne gère pas CHLAUTH/OAM, le cycle de vie complet des gestionnaires ni les commandes MQSC arbitraires.

## 8. TLS, LDAP et autorisations

Maintenir la vérification des certificats pour REST et le transport MQ. Le laboratoire utilise une autorité de certification d'évaluation privée avec un certificat serveur distinct et des clés protégées. Ne jamais versionner les clés. Examiner séparément la confiance client, CHLAUTH, CONNAUTH, LDAP et OAM.

Ne pas désactiver la vérification du nom d'hôte, ouvrir largement le pare-feu ou attribuer `mqm` par défaut pour faire réussir un test. Réaliser les tests de refus dans un environnement isolé.

## 9. Audits et tests

Exécuter `python3 -m unittest discover -s tests -v` et les contrôles de syntaxe Ansible. L'audit d'un gestionnaire exige une autorisation explicite pour les mutations et produit des preuves avec SHA-256. Les contrôles de topologie nécessitent une acceptation séparée.

Les tests hors ligne et simulés ne prouvent pas la compatibilité IBM MQ. Marquer NOT TESTED les scénarios réels non exécutés. Enregistrer le système, la version MQ, la révision Git, le résultat et les preuves.

## 10. Exploitation et dépannage

Examiner successivement la connexion du contrôleur, le compte système, l'état du gestionnaire, l'installation sélectionnée, la chaîne de certificats, les autorités MQ et les journaux. Pour le laboratoire, consulter `journalctl -u bergen-mq-lab.service` et les journaux d'erreurs MQ.

Pour HTTP 401/403, vérifier l'identité, l'autorité de certification et l'en-tête CSRF, sans désactiver les protections. En cas d'échec MQSC, lire les rapports JSON protégés sous `ansible/reports/mqsc/` et ne pas rejouer aveuglément un changement partiellement appliqué.

## 11. Sauvegarde, restauration et retour arrière

Sauvegarder les données persistantes MQ, la configuration, les certificats et les copies hors site selon la politique locale. Recréer un conteneur n'est pas une sauvegarde. Prévoir un point de restauration vérifié avant toute suppression.

MQSC ne fournit ni transaction globale ni rollback automatique. Préparer les commandes inverses et vérifier l'état réel avant de réessayer. Tester séparément la restauration, le redémarrage et les objectifs de reprise.

## 12. Sécurité, gouvernance et limites

Les exemples du laboratoire sont réservés à l'évaluation. La production exige une autorisation IBM de licence, de sécurité, de changement et de compatibilité indépendante. Protéger Vault, les rapports et les fichiers MQSC. Chaque modification doit être revue et associée à une cible et un identifiant précis.

L'adaptateur actuel ne gère pas l'exécution native dans un conteneur, les anciennes versions MQ sans les options requises de `runmqsc`, les verrous distribués ou la garantie d'exécution unique. Le processus de livraison doit gérer approbation, maintenance, sauvegardes et validation par plateforme.

---

Références techniques / Technische Referenzen: [README](https://github.com/tobe4it/bergen-mq-lab/blob/main/README.md) · [Lab](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-LAB.md) · [REST](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ.md) · [MQSC](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md) · [Audit](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-AUDIT.md) · [Topology](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQ-TOPOLOGY.md).
