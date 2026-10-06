# Infrastructure (AWS)

[![English](https://img.shields.io/badge/lang-English-lightgrey)](../en/INFRA.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](INFRA.md)

Votely tourne sur AWS, en **eu-west-1 (Irlande)**. Tout est décrit avec Terraform dans
`infra/terraform/` ; rien n'est créé ni modifié à la main dans la console, qui ne sert qu'à
regarder.

```
infra/terraform/
├── .tflint.hcl     # règles de lint communes à toutes les stacks (Terraform + AWS)
└── bootstrap/      # bucket du state distant et alerte budget mensuelle
```

Chaque dossier est une **stack** séparée, avec son propre state et son propre cycle de vie : le
bootstrap est créé une fois et conservé, le serveur est créé et détruit à volonté.

## Accès à AWS

| Qui | Comment | Secret permanent |
|---|---|---|
| Une personne | IAM Identity Center : portail d'accès avec mot de passe + MFA, identifiants temporaires pour la CLI | aucun |
| L'utilisateur root | Uniquement pour les rares tâches de compte qui l'exigent ; protégé par MFA | – |

La CLI utilise un profil SSO (`~/.aws/config`, en dehors du dépôt) :

```ini
[sso-session votely]
sso_start_url = https://<id-du-portail>.awsapps.com/start
sso_region = eu-west-1
sso_registration_scopes = sso:account:access

[profile votely]
sso_session = votely
sso_account_id = <id du compte>
sso_role_name = AdministratorAccess
region = eu-west-1
```

```bash
aws sso login --profile votely      # ouvre le navigateur : mot de passe + MFA, valable 8 heures
export AWS_PROFILE=votely
aws sts get-caller-identity         # qui suis-je ? (lecture seule)
```

Aucune clé d'accès n'est jamais créée : les identifiants expirent d'eux-mêmes et rien sur le
disque ne peut fuiter. L'identifiant du compte n'est pas écrit dans le dépôt non plus.

## Bootstrap : state Terraform et budget

Terraform tient un registre de ce qu'il gère, le **state**, et le compare au code pour savoir
quoi créer, modifier ou supprimer. Le state contient le détail des ressources et parfois des
secrets : il ne va jamais dans Git, il est rangé dans un bucket S3 dédié.

| Réglage | Pourquoi |
|---|---|
| Versioning | Chaque modification garde la version précédente : un mauvais apply peut être annulé |
| Chiffrement (SSE-S3) | Données chiffrées au repos |
| Accès public bloqué, propriété imposée | Le bucket n'est accessible que via IAM |
| HTTPS uniquement (politique du bucket) | Aucune requête non chiffrée acceptée |
| Anciennes versions supprimées après 90 jours | Un historique, sans croissance infinie |
| `prevent_destroy` | Terraform refuse de supprimer le bucket |
| `use_lockfile` | Verrou natif S3 : deux `apply` ne peuvent jamais tourner en même temps (plus besoin de table DynamoDB) |

Le nom du bucket a un suffixe aléatoire (`votely-tfstate-08da0d86`) : les noms de bucket sont
uniques au monde, et l'identifiant du compte reste en dehors du dépôt.

L'**alerte budget** (`votely-monthly`, 10 USD par mois) envoie un email à 80 % et à 100 % des
coûts réels, et dès qu'AWS prévoit un dépassement sur le mois. L'adresse vient de
`terraform.tfvars`, ignoré par Git (`terraform.tfvars.example` montre le format).

### Premier lancement : le state déménage dans son propre bucket

Le bootstrap range son state dans le bucket qu'il crée : le bucket doit donc exister d'abord.

```bash
cd infra/terraform/bootstrap
cp terraform.tfvars.example terraform.tfvars   # puis renseigner budget_email

# 1. Créer le bucket avec un state local (backend_override.tf est ignoré par Git)
printf 'terraform {\n  backend "local" {}\n}\n' > backend_override.tf
terraform init
terraform plan -out=bootstrap.tfplan
terraform apply bootstrap.tfplan

# 2. Déménager le state dans le bucket
rm backend_override.tf
terraform init -migrate-state                  # répondre "yes"
rm terraform.tfstate bootstrap.tfplan          # les copies locales ne servent plus
terraform plan                                 # "No changes" : code, state et AWS correspondent
```

`terraform plan -out` enregistre le plan relu, et `terraform apply <fichier>` applique exactement
ce plan : si quelque chose a changé entre-temps, Terraform refuse le plan périmé au lieu de faire
autre chose.

## Vérifications

```bash
cd infra/terraform
terraform fmt -recursive -check
terraform -chdir=bootstrap validate
tflint --init --config="$PWD/.tflint.hcl"
tflint --chdir=bootstrap --config="$PWD/.tflint.hcl"
```

Les versions des providers sont verrouillées dans `.terraform.lock.hcl` pour Linux et macOS : chaque
machine et la CI utilisent les mêmes builds.

## Coûts

| Ressource | Coût |
|---|---|
| Bucket du state (quelques Ko) | quelques centimes par an |
| Alerte budget | gratuite (les deux premiers budgets d'un compte sont gratuits) |
