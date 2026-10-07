#!/usr/bin/env bash
# Install (or upgrade) Argo CD on the AWS server. Needs the tunnel (tunnel.sh) and the kubeconfig
# (fetch-kubeconfig.sh). Once Argo CD runs, the cluster content is described in Git.
set -euo pipefail
cd "$(dirname "$0")/../.."

ARGOCD_CHART_VERSION=10.9.7 # Argo CD v3.5.4

[ "$(kubectl config current-context)" = votely-aws ] || { echo "Use the votely-aws kubeconfig." >&2; exit 1; }

helm upgrade --install argocd argo-cd --repo https://argoproj.github.io/argo-helm \
  --version "$ARGOCD_CHART_VERSION" --namespace argocd --create-namespace \
  --values deploy/platform/argocd/values.yaml --wait

echo "Argo CD is running. Open the UI with: deploy/aws/argocd-ui.sh"
