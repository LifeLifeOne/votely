# Intégration continue

[![English](https://img.shields.io/badge/lang-English-lightgrey)](../en/CI.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](CI.md)

Votely est construit et testé par GitLab CI à chaque merge request et à chaque commit sur
`main`. Pipelines : https://gitlab.com/StateOfFlowHunter/votely/-/pipelines

## Organisation

```
.gitlab-ci.yml                  # point d'entrée : workflow, stages, valeurs par défaut, includes
.gitlab/ci/
├── templates.gitlab-ci.yml     # briques communes (build Docker, règles)
├── backend.gitlab-ci.yml       # jobs backend:*
├── frontend.gitlab-ci.yml      # jobs frontend:*
└── e2e.gitlab-ci.yml           # jobs e2e:*
```

- Un fichier par composant : tout ce qui concerne le pipeline du backend est au même endroit,
  et les stages sont déclarés une seule fois dans `.gitlab-ci.yml`.
- Le suffixe `.gitlab-ci.yml` permet aux éditeurs et aux outils GitLab de reconnaître et valider
  les fichiers.
- Les jobs sont nommés `<composant>:<action>` (`backend:lint`, `frontend:lint`) : le graphe du
  pipeline se lit d'un coup d'œil.
- Chaque fichier commence par un job caché (`.backend`, `.frontend`, `.e2e`) qui porte l'image,
  le cache et les règles communs aux jobs du composant, qui l'étendent avec `extends`.

## Quand les pipelines tournent

| Événement | Pipeline | Jobs |
|---|---|---|
| Merge request | oui | uniquement les composants dont les fichiers (ou le fichier CI) ont changé |
| Push sur une branche avec une merge request ouverte | non (le pipeline de la merge request la couvre) | – |
| Push sur `main` | oui | tous les jobs |
| Tag | oui | tous les jobs |

Filtrer les jobs des merge requests selon les fichiers modifiés garde des pipelines rapides et
économise les minutes de CI ; `main` lance toujours tout, donc la branche principale est
toujours entièrement vérifiée.

Un nouveau push annule le pipeline en cours sur la même branche (jobs `interruptible`). Les jobs
ne sont relancés qu'une fois, et uniquement en cas de panne d'infrastructure, jamais pour un test
ou un lint en échec.

## Stages

| Stage | Job | Ce qu'il vérifie |
|---|---|---|
| `lint` | `backend:lint` | ruff (règles de lint, ordre des imports) et ruff format |
| | `frontend:lint` | oxlint (les avertissements font échouer le job), Prettier, TypeScript |
| | `e2e:lint` | Prettier, TypeScript |
| `test` | `backend:test` | pytest : tests unitaires et d'intégration face à un service PostgreSQL 16, migrations comprises ; couverture ≥ 90 % |
| | `frontend:test` | Vitest : composants et pages face à une fausse API (MSW) ; couverture ≥ 80 % des lignes |
| `build` | `backend:build`, `frontend:build` | Images de production construites et poussées dans le registry de conteneurs GitLab |

Chaque job de test n'attend que le lint de son propre composant (`needs`) : un lint frontend lent
ne retarde jamais les tests du backend.

`backend:test` tourne avec `CI=true` (toujours défini par GitLab) : si PostgreSQL était
injoignable, les tests d'intégration échoueraient au lieu d'être ignorés comme en local.

## Images de conteneurs

Les images sont poussées dans le registry de conteneurs du projet :
`registry.gitlab.com/stateofflowhunter/votely/<composant>:<SHA du commit>`.

- **Tags immuables** : le SHA complet du commit identifie exactement ce qui a été construit. Les
  tags de déploiement (`main`, versions) sont ajoutés plus tard, une fois les images testées.
- **Jamais sans tests** : chaque job de build dépend (`needs`) des tests de son composant ; un
  test en échec empêche la publication de l'image.
- **Les deux images, ou aucune** : les builds tournent dès qu'un chemin applicatif change
  (`.rules:app`), pour que les tests end-to-end utilisent toujours un backend et un frontend du
  même commit. Reconstruire une image inchangée est rapide grâce au cache des couches.
- **Cache des couches dans le registry** (`:buildcache`, BuildKit `mode=max`) : écrit uniquement
  par la branche principale, lu par tous les pipelines.
- **Traçabilité** : des labels OCI enregistrent le dépôt source, le commit et la date de build.
- **Digest transmis aux jobs suivants** : chaque build exporte `BACKEND_IMAGE` /
  `FRONTEND_IMAGE` (`…@sha256:…`) en artefact dotenv ; les jobs suivants utilisent exactement
  l'image construite, pas un tag qui pourrait bouger.

Les builds utilisent Docker-in-Docker avec BuildKit (`docker buildx`), la configuration standard
sur les runners partagés de GitLab.com.

## Rapports

| Rapport | Où il apparaît |
|---|---|
| JUnit (`junit.xml`) | Onglet *Tests* du pipeline, et widget de la merge request (nouveaux échecs, tests corrigés) |
| Pourcentage de couverture | Widget de la merge request et liste des jobs, extrait du log du job |
| Cobertura (`coverage.xml`) | Lignes couvertes et non couvertes surlignées dans le diff de la merge request |

Les rapports sont envoyés même quand les tests échouent (`when: always`) et conservés une semaine.

## Cache

Les dépendances sont mises en cache par composant, avec le fichier de verrouillage comme clé
(`uv.lock`, `package-lock.json`) : le cache est réutilisé tant que les dépendances ne changent
pas. Les fichiers de verrouillage sont toujours respectés (`UV_FROZEN`, `npm ci`) : la CI
n'installe jamais autre chose que ce qui a été relu.

## Images

| Composant | Image CI |
|---|---|
| Backend | `ghcr.io/astral-sh/uv:0.12-python3.12-trixie-slim` (même Python et même Debian que l'image de production) |
| Frontend, e2e | `node:24-alpine` |
