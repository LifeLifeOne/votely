# Backend

[![English](https://img.shields.io/badge/lang-English-lightgrey)](../en/BACK.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](BACK.md)

API REST écrite en Python 3.12 avec FastAPI, SQLAlchemy 2 et PostgreSQL 16.
Les dépendances sont gérées avec [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

## Architecture

Le code est découpé en trois couches. Les dépendances pointent uniquement vers l'intérieur :
l'API connaît le domaine, le domaine ne connaît que les contrats des repositories.

```
backend/app/
├── api/            # Couche HTTP : routes, schémas, dépendances d'authentification, erreurs
├── domain/         # Règles métier (PollService, UserService) et erreurs du domaine
├── repositories/   # Persistance : modèles SQLAlchemy et repositories SQL
└── core/           # Transverse : configuration, session base de données, sécurité, logs
```

| Couche | Responsabilité | Exemple |
|---|---|---|
| `api` | Valider la forme des entrées, authentifier, appeler le service, sérialiser la réponse | `PollCreate` exige 2 à 10 options uniques |
| `domain` | Règles qui dépendent du temps ou des données stockées | voter sur un sondage fermé est refusé |
| `repositories` | Requêtes SQL, transactions, violations de contraintes | un vote en double devient `AlreadyVotedError` |

Les services dépendent de **protocoles** de repository (`PollRepository`, `UserRepository`),
pas directement de SQLAlchemy. Les tests unitaires injectent des faux en mémoire
(`tests/unit/fakes.py`) et une horloge fixe : les règles métier sont testées en quelques
millisecondes, sans base de données.

Les erreurs du domaine sont de simples exceptions Python (`app/domain/errors.py`), traduites en
codes HTTP à un seul endroit (`app/api/errors.py`).

## Authentification

Les comptes sont locaux (email + mot de passe). Après connexion, la session est un JWT signé
stocké dans un cookie ; le navigateur l'envoie automatiquement, le frontend ne manipule jamais
le token.

| Mesure | Pourquoi |
|---|---|
| Mots de passe hachés en **Argon2id** (`pwdlib`) | Algorithme coûteux en mémoire, résistant au cassage sur GPU |
| Mot de passe de 12 à 128 caractères | La longueur compte plus que les règles de complexité |
| Emails stockés en minuscules, contrainte d'unicité | `Alice@x.com` et `alice@x.com` sont le même compte |
| Même erreur et même temps de réponse pour un email inconnu ou un mauvais mot de passe | La connexion ne permet pas de découvrir les comptes existants |
| JWT **HS256**, signé avec `VOTELY_JWT_SECRET` (≥ 32 caractères, obligatoire) | L'application refuse de démarrer avec une clé absente ou faible |
| Token de courte durée (`exp`, 60 min par défaut) | Limite l'impact d'un token volé |
| Cookie `HttpOnly` | Illisible par JavaScript, donc impossible à voler via une faille XSS |
| Cookie `SameSite=Lax` | Non envoyé sur les requêtes POST d'un autre site, ce qui bloque le CSRF |
| Cookie `Secure` (par défaut) | Envoyé uniquement en HTTPS ; désactivé explicitement pour le HTTP local |

Droits :

| Action | Anonyme | Connecté |
|---|---|---|
| Lister / consulter les sondages et résultats | ✅ | ✅ |
| Créer un sondage (l'utilisateur en devient l'auteur) | ❌ `401` | ✅ |
| Voter | ❌ `401` | ✅ une fois par sondage |

### Un vote par utilisateur et par sondage

La règle est garantie par une **contrainte d'unicité** `(poll_id, user_id)` sur `votes`, pas
seulement par une vérification en Python : deux requêtes simultanées pourraient toutes deux
passer un test « cet utilisateur a-t-il déjà voté ? », mais une seule insertion peut respecter
la contrainte. Le repository traduit la violation de cette contrainte précise en
`AlreadyVotedError` (`409`). Un vote est définitif.

Chaque sondage est renvoyé avec `has_voted`, pour que le frontend puisse désactiver le bouton de
vote ; il est calculé en une seule requête pour toute une page de sondages.

## API

Tous les endpoints métier sont versionnés sous `/api/v1`. La documentation interactive est
générée par FastAPI sur `/docs` (Swagger UI) et `/redoc`.

| Méthode | Chemin | Auth | Description | Succès |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | – | Créer un compte | `201` |
| `POST` | `/api/v1/auth/login` | – | Ouvrir une session (pose le cookie) | `204` |
| `POST` | `/api/v1/auth/logout` | – | Fermer la session (supprime le cookie) | `204` |
| `GET` | `/api/v1/auth/me` | requise | Utilisateur courant | `200` |
| `POST` | `/api/v1/polls` | requise | Créer un sondage | `201` |
| `GET` | `/api/v1/polls?limit=20&offset=0` | optionnelle | Lister les sondages, du plus récent au plus ancien | `200` |
| `GET` | `/api/v1/polls/{id}` | optionnelle | Consulter un sondage et ses options | `200` |
| `POST` | `/api/v1/polls/{id}/votes` | requise | Voter pour une option | `204` |
| `GET` | `/api/v1/polls/{id}/results` | – | Nombre de votes et pourcentages | `200` |
| `GET` | `/healthz` | – | Sonde de liveness (ne touche jamais la base) | `200` |
| `GET` | `/readyz` | – | Sonde de readiness (`SELECT 1`) | `200` / `503` |

Exemple de session avec curl :

```bash
curl -X POST localhost:8000/api/v1/auth/register -H 'content-type: application/json' \
  -d '{"email": "alice@example.com", "password": "correct horse battery"}'
curl -c cookies.txt -X POST localhost:8000/api/v1/auth/login -H 'content-type: application/json' \
  -d '{"email": "alice@example.com", "password": "correct horse battery"}'
curl -b cookies.txt -X POST localhost:8000/api/v1/polls -H 'content-type: application/json' \
  -d '{"question": "Where should we deploy?", "options": ["AWS", "GCP", "Azure"]}'
```

### Erreurs

| Statut | Quand |
|---|---|
| `401` | Non connecté, session invalide ou expirée, identifiants incorrects |
| `404` | Sondage inconnu |
| `409` | Email déjà utilisé, sondage fermé, utilisateur ayant déjà voté |
| `422` | Données invalides, option n'appartenant pas au sondage, date de fermeture passée |

Le corps d'une erreur a toujours la forme `{"detail": ...}`.

## Modèle de données

```mermaid
erDiagram
    users ||--o{ polls : authors
    users ||--o{ votes : casts
    polls ||--|{ options : has
    polls ||--o{ votes : receives
    options ||--o{ votes : counts
```

| Table | Notes |
|---|---|
| `users` | Clé primaire UUID, `email` unique en minuscules, `password_hash` Argon2 |
| `polls` | Clé primaire UUID, `author_id` (mis à `NULL` si l'utilisateur est supprimé), `closes_at` optionnel, `created_at` indexé |
| `options` | Triées par `position`, uniques par sondage, supprimées avec leur sondage |
| `votes` | Identité `BIGINT`, `poll_id` + `option_id` + `user_id`, unicité `(poll_id, user_id)` |

Les identifiants publics sont des UUID, pour qu'on ne puisse pas les deviner par énumération.
Les noms de contraintes suivent une convention de nommage (`app/repositories/models.py`) : les
migrations restent déterministes, et le code peut reconnaître la violation d'une contrainte
précise.

`polls.author_id` et `votes.user_id` sont volontairement nullables : les données créées avant
l'arrivée des comptes sont conservées plutôt que supprimées par une migration.

## Configuration

La configuration est lue depuis des variables d'environnement préfixées par `VOTELY_`
(12-factor), avec un fichier `.env` optionnel pour le développement local. Une configuration
invalide arrête l'application au démarrage.

| Variable | Défaut | Description |
|---|---|---|
| `VOTELY_DATABASE_URL` | `postgresql+psycopg://votely:votely@localhost:5432/votely` | URL SQLAlchemy |
| `VOTELY_JWT_SECRET` | – (**obligatoire**, ≥ 32 caractères) | Clé de signature des sessions, ex. `openssl rand -hex 32` |
| `VOTELY_ACCESS_TOKEN_TTL_MINUTES` | `60` | Durée de vie d'une session |
| `VOTELY_COOKIE_SECURE` | `true` | À passer à `false` uniquement en développement local en HTTP |
| `VOTELY_LOG_LEVEL` | `INFO` | Niveau de log Python |

## Migrations de base de données

Les évolutions du schéma sont gérées avec Alembic (`backend/alembic/`).

```bash
uv run alembic upgrade head                                  # appliquer les migrations
uv run alembic revision --autogenerate -m "add poll author"  # créer une migration
uv run alembic downgrade -1                                  # revenir d'une étape
```

Les migrations autogénérées doivent toujours être relues : Alembic ne connaît pas les données
existantes. Par exemple, `one vote per user and poll` ajoute `votes.poll_id` en nullable, le
remplit à partir de `options`, puis seulement le passe en `NOT NULL` ; la version générée aurait
échoué sur toute base contenant déjà des votes.

## Tests

```bash
docker compose up -d db   # les tests d'intégration ont besoin de PostgreSQL
uv run pytest             # unitaires + intégration, avec couverture (minimum 90 %)
uv run pytest tests/unit  # rapides, sans base de données
```

- **Tests unitaires** (`tests/unit`) : règles métier, validation des schémas, configuration,
  hachage des mots de passe et tokens, sans I/O.
- **Tests d'intégration** (`tests/integration`) : appels HTTP sur un vrai PostgreSQL, avec des
  clients anonymes et connectés (fixture `login_as`). Ils utilisent une base dédiée
  `<db>_test`, créée automatiquement et migrée avec Alembic : les migrations sont testées à
  chaque lancement ; les tables sont vidées entre chaque test.
- **Test de migration** : revient à un schéma antérieur, insère des données existantes,
  remigre et vérifie que les données ont survécu.

Sans PostgreSQL, les tests d'intégration sont ignorés en local ; en CI (variable `CI`
définie), ils échouent, pour qu'une base mal configurée ne passe jamais inaperçue.

## Limites connues

- Pas encore de limitation du nombre de tentatives sur la connexion et l'inscription
  (protection contre la force brute).
- Pas de vérification d'email ni de réinitialisation du mot de passe.
- Les sessions ne peuvent pas être révoquées côté serveur avant leur expiration : la
  déconnexion supprime le cookie du navigateur, d'où des tokens de courte durée.
