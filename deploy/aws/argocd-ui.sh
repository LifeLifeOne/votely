#!/usr/bin/env bash
# Open the Argo CD web UI on http://localhost:8080 through the tunnel (tunnel.sh must run).
# Ctrl+C closes it.
set -euo pipefail

[ "$(kubectl config current-context)" = votely-aws ] || { echo "Use the votely-aws kubeconfig." >&2; exit 1; }

# The initial admin password exists until it is changed and the Secret deleted.
if password=$(kubectl --namespace argocd get secret argocd-initial-admin-secret \
  --output jsonpath='{.data.password}' 2>/dev/null); then
  echo "Login: admin / $(printf '%s' "$password" | base64 --decode)"
fi
echo "Argo CD: http://localhost:8080"
exec kubectl --namespace argocd port-forward service/argocd-server 8080:80
