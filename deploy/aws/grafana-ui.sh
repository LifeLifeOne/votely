#!/usr/bin/env bash
# Open Grafana on http://localhost:3000 through the tunnel (tunnel.sh must run).
# Ctrl+C closes it.
set -euo pipefail

[ "$(kubectl config current-context)" = votely-aws ] || { echo "Use the votely-aws kubeconfig." >&2; exit 1; }

# The credentials are the sealed Secret that Argo CD deployed: read from the cluster, never from Git.
read_key() {
  kubectl --namespace monitoring get secret grafana-admin --output "jsonpath={.data.$1}" | base64 --decode
}
echo "Login: $(read_key admin-user) / $(read_key admin-password)"
echo "Grafana: http://localhost:3000"
exec kubectl --namespace monitoring port-forward service/monitoring-grafana 3000:80
