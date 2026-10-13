# Observability

[![English](https://img.shields.io/badge/lang-English-blue)](OBSERVABILITY.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-lightgrey)](../fr/OBSERVABILITY.md)

The cluster watches itself. Three tools, deployed by Argo CD like everything else:

| Tool | Role |
|---|---|
| **Prometheus** | Reads the metrics of every pod and of the node every 30 seconds, and keeps three days of history |
| **Grafana** | Draws the metrics as dashboards |
| **Alertmanager** | Groups and shows the alerts that Prometheus raises |

They come from the [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
chart, in the `monitoring` namespace: [`deploy/argocd/apps/monitoring.yaml`](../../deploy/argocd/apps/monitoring.yaml)
(application, wave -1) and [`deploy/platform/monitoring/values.yaml`](../../deploy/platform/monitoring/values.yaml)
(settings).

## Settings worth knowing

- **k3s.** The control plane runs inside one process and exposes no separate metrics endpoint
  for the scheduler, the controller manager, etcd or kube-proxy: scraping them is turned off, or
  they would raise alerts that never clear.
- **Every ServiceMonitor and rule is picked up**, whatever its release label: the application's
  own monitoring lives in its chart and is discovered without any change to the stack.
- **A short history** (3 days, 3 GB at most, on a 5 GiB volume of the persistent data disk).
- **Stateless Grafana.** Dashboards are files in Git, loaded from ConfigMaps: nothing is built by
  hand, and a new cluster has them straight away.
- **Memory limits** on every component: the node is shared with the two environments. Grafana
  gets 512 MiB: it was `OOMKilled` at 256 MiB while loading the dashboards of the chart.

## What the API exposes

`GET /metrics` on the backend, in the Prometheus format (about 200 series per pod):

| Metric | Meaning |
|---|---|
| `http_requests_total` | Requests by method, route and status class (`2xx`, `4xx`, `5xx`) |
| `http_request_duration_highr_seconds` | Duration of each request, as a histogram: latency percentiles |
| `votely_votes_total` | Votes recorded: the business metric. A rejected vote is not counted |

- **Bounded cardinality.** Requests are grouped by route *template* (`/api/v1/polls/{poll_id}`),
  never by the real URL, and unknown URLs fall into one `none` group: scanners cannot make the
  number of series grow.
- **Probes are left out** (`/healthz`, `/readyz`): they would drown the traffic figures.
- **Not public.** The frontend proxy only forwards `/api/`, so the page is reachable inside the
  cluster, where Prometheus reads it, and nowhere else. A platform test checks it.
- **Discovery.** A `ServiceMonitor` in the `votely` chart (`metrics.enabled`) tells Prometheus
  where to look. It is off by default, because the local cluster has no monitoring stack.

## The Votely dashboard

[`dashboard-votely.yaml`](../../deploy/platform/monitoring/dashboard-votely.yaml) is a ConfigMap
labelled `grafana_dashboard`: Grafana's sidecar finds it and loads the **Votely** dashboard on its
own. It is read-only in Grafana (the JSON in Git is the source) and has an *Environment* selector
(staging, production, or both).

| Panel | Query it answers |
|---|---|
| Requests per second, Error rate (5xx), Latency p95, Votes (24 h), Backend pods available | How is the application doing right now? |
| Requests per second, Latency (p50, p95, p99) | Traffic and response time over time |
| Server errors, Votes per minute | What goes wrong, and what users do |
| Memory by pod, Container restarts | Is a pod close to its limit, or dying? |

With no traffic, the stats say *no traffic* instead of showing `NaN`, and the server errors panel
stays on a flat zero line. *Backend pods available* turns red at 0: it is what the first alert
below measures.

## Alerts

[`alerts.yaml`](../../deploy/platform/monitoring/alerts.yaml) is a `PrometheusRule`: Prometheus
evaluates it every 30 seconds, Alertmanager shows what fires (Grafana: *Alerting*; no notification
is sent). Four symptoms a user would notice:

| Alert | Fires when | After | Severity |
|---|---|---|---|
| `VotelyBackendUnavailable` | no backend pod is available in an environment | 1 min | critical |
| `VotelyHighErrorRate` | more than 5 % of the responses are 5xx | 5 min | warning |
| `VotelySlowRequests` | the p95 response time exceeds 1 s | 10 min | warning |
| `VotelyPodRestartingOften` | a container restarted more than 3 times in 15 minutes | immediately | warning |

The first one counts pods (`kube_deployment_status_replicas_available`) rather than scrapes: a
stopped pod leaves no metrics behind, so an alert based on `up` would never fire. `Watchdog`, an
alert that always fires, comes with the stack: it proves the alerting chain is alive.

## Access

Nothing is exposed on the internet. Through the Systems Manager tunnel:

```bash
deploy/aws/tunnel.sh        # terminal 1
deploy/aws/grafana-ui.sh    # terminal 2: prints the login, opens http://localhost:3000
```

The admin credentials are generated and sealed by `deploy/aws/seal-secrets.sh monitoring`
([GITOPS.md](GITOPS.md#secrets)): a password generated by the chart would change at every Argo CD
render. `grafana-ui.sh` reads them from the cluster, never from Git.
