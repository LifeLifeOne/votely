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
  environnements.

## Accès

Rien n'est exposé sur Internet. Via le tunnel Systems Manager :

```bash
deploy/aws/tunnel.sh        # terminal 1
deploy/aws/grafana-ui.sh    # terminal 2 : affiche l'identifiant, ouvre http://localhost:3000
```

Les identifiants admin sont générés et chiffrés par `deploy/aws/seal-secrets.sh monitoring`
([GITOPS.md](GITOPS.md#secrets)) : un mot de passe généré par le chart changerait à chaque rendu
d'Argo CD. `grafana-ui.sh` les lit dans le cluster, jamais dans Git.
