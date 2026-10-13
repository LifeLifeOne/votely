# Observabilité

[![English](https://img.shields.io/badge/lang-English-lightgrey)](../en/OBSERVABILITY.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](OBSERVABILITY.md)

Le cluster se surveille lui-même. Trois outils, déployés par Argo CD comme le reste :

| Outil | Rôle |
|---|---|
| **Prometheus** | Lit les métriques de chaque pod et du nœud toutes les 30 secondes, et garde trois jours d'historique |
| **Grafana** | Dessine les métriques sous forme de tableaux de bord |
| **Alertmanager** | Regroupe et affiche les alertes que Prometheus déclenche |

Ils viennent du chart [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack),
dans le namespace `monitoring` : [`deploy/argocd/apps/monitoring.yaml`](../../deploy/argocd/apps/monitoring.yaml)
(application, vague -1) et [`deploy/platform/monitoring/values.yaml`](../../deploy/platform/monitoring/values.yaml)
(réglages).

## Réglages à connaître

- **k3s.** Le plan de contrôle tourne dans un seul processus et n'expose pas de point de
  métriques séparé pour le scheduler, le controller manager, etcd ou kube-proxy : leur collecte est
  désactivée, sinon elle déclencherait des alertes qui ne s'éteindraient jamais.
- **Tous les ServiceMonitor et toutes les règles sont pris en compte**, quel que soit leur label
  de release : la surveillance propre à l'application vit dans son chart et est découverte sans
  rien changer à la pile.
- **Un historique court** (3 jours, 3 Go au plus, sur un volume de 5 Gio du disque de données
  permanent).
- **Grafana sans état.** Les tableaux de bord sont des fichiers dans Git, chargés depuis des
  ConfigMaps : rien n'est construit à la main, et un nouveau cluster les a tout de suite.
- **Des limites de mémoire** sur chaque composant : le nœud est partagé avec les deux
  environnements. Grafana a 512 Mio : il était tué (`OOMKilled`) à 256 Mio en chargeant les
  tableaux de bord du chart.

## Ce que l'API expose

`GET /metrics` sur le backend, au format Prometheus (environ 200 séries par pod) :

| Métrique | Signification |
|---|---|
| `http_requests_total` | Requêtes par méthode, route et classe de statut (`2xx`, `4xx`, `5xx`) |
| `http_request_duration_highr_seconds` | Durée de chaque requête, en histogramme : les percentiles de latence |
| `votely_votes_total` | Votes enregistrés : la métrique métier. Un vote refusé n'est pas compté |

- **Cardinalité bornée.** Les requêtes sont regroupées par *modèle* de route
  (`/api/v1/polls/{poll_id}`), jamais par l'URL réelle, et les URL inconnues tombent dans un seul
  groupe `none` : un scanner ne peut pas faire grossir le nombre de séries.
- **Les sondes sont exclues** (`/healthz`, `/readyz`) : elles noieraient les chiffres du trafic.
- **Pas public.** Le proxy du frontend ne transmet que `/api/` : la page est joignable dans le
  cluster, où Prometheus la lit, et nulle part ailleurs. Un test de plateforme le vérifie.
- **Découverte.** Un `ServiceMonitor` dans le chart `votely` (`metrics.enabled`) indique à
  Prometheus où regarder. Il est désactivé par défaut, car le cluster local n'a pas la pile de
  monitoring.

## Le tableau de bord Votely

[`dashboard-votely.yaml`](../../deploy/platform/monitoring/dashboard-votely.yaml) est un ConfigMap
avec le label `grafana_dashboard` : le sidecar de Grafana le trouve et charge tout seul le
tableau de bord **Votely**. Il est en lecture seule dans Grafana (la source est le JSON dans Git) et
a un sélecteur *Environment* (staging, production, ou les deux).

| Panneau | Question à laquelle il répond |
|---|---|
| Requests per second, Error rate (5xx), Latency p95, Votes (24 h), Backend pods available | Comment va l'application en ce moment ? |
| Requests per second, Latency (p50, p95, p99) | Trafic et temps de réponse dans le temps |
| Server errors, Votes per minute | Ce qui va mal, et ce que font les utilisateurs |
| Memory by pod, Container restarts | Un pod est-il près de sa limite, ou en train de mourir ? |

Sans trafic, les compteurs affichent *no traffic* au lieu de `NaN`, et le panneau des erreurs
serveur reste sur une ligne à zéro. *Backend pods available* devient rouge à 0 : c'est ce que
mesure la première alerte ci-dessous.

## Alertes

[`alerts.yaml`](../../deploy/platform/monitoring/alerts.yaml) est une `PrometheusRule` : Prometheus
l'évalue toutes les 30 secondes, Alertmanager affiche ce qui se déclenche (Grafana : *Alerting* ;
aucune notification n'est envoyée). Quatre symptômes que verrait un utilisateur :

| Alerte | Se déclenche quand | Après | Gravité |
|---|---|---|---|
| `VotelyBackendUnavailable` | aucun pod du backend n'est disponible dans un environnement | 1 min | critical |
| `VotelyHighErrorRate` | plus de 5 % des réponses sont des 5xx | 5 min | warning |
| `VotelySlowRequests` | le temps de réponse p95 dépasse 1 s | 10 min | warning |
| `VotelyPodRestartingOften` | un conteneur a redémarré plus de 3 fois en 15 minutes | tout de suite | warning |

La première compte les pods (`kube_deployment_status_replicas_available`) plutôt que les
collectes : un pod arrêté ne laisse aucune métrique derrière lui, donc une alerte basée sur `up` ne
se déclencherait jamais. `Watchdog`, une alerte qui sonne en permanence, vient avec la pile : elle
prouve que la chaîne d'alerte est vivante.

## Tester une alerte

Une alerte qui ne s'est jamais déclenchée n'est pas prouvée. Pour déclencher
`VotelyBackendUnavailable` sur staging, on arrête son backend. Argo CD défend ce que dit Git **à
deux niveaux** : `staging-votely` répare le déploiement, et `root` (l'app of apps) répare
l'`Application` elle-même en quelques secondes. Il faut suspendre les deux, sinon le test s'arrête
avant que l'alerte ait le temps de se déclencher :

```bash
kubectl -n argocd patch application root --type merge \
  -p '{"spec":{"syncPolicy":{"automated":{"selfHeal":false}}}}'
kubectl -n argocd patch application staging-votely --type merge \
  -p '{"spec":{"syncPolicy":{"automated":{"selfHeal":false}}}}'
kubectl -n votely-staging scale deployment votely-backend --replicas=0
```

Mesuré : *Pending* 36 secondes après l'arrêt, *Firing* au bout de 1 minute 38 (le `for: 1m` de la
règle plus l'intervalle d'évaluation). Puis on répare, dans l'autre sens :

```bash
kubectl -n votely-staging scale deployment votely-backend --replicas=1
kubectl -n argocd patch application root --type merge \
  -p '{"spec":{"syncPolicy":{"automated":{"selfHeal":true}}}}'
kubectl -n argocd patch application staging-votely --type merge \
  -p '{"spec":{"syncPolicy":{"automated":{"selfHeal":true}}}}'
```

L'alerte s'éteint environ une minute après le retour du backend.

## Accès

Rien n'est exposé sur Internet. Via le tunnel Systems Manager :

```bash
deploy/aws/tunnel.sh        # terminal 1
deploy/aws/grafana-ui.sh    # terminal 2 : affiche l'identifiant, ouvre http://localhost:3000
```

Les identifiants admin sont générés et chiffrés par `deploy/aws/seal-secrets.sh monitoring`
([GITOPS.md](GITOPS.md#secrets)) : un mot de passe généré par le chart changerait à chaque rendu
d'Argo CD. `grafana-ui.sh` les lit dans le cluster, jamais dans Git.
