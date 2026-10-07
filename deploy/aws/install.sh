#!/usr/bin/env bash
# Install Votely on the AWS server: cert-manager and its Let's Encrypt issuers, the Secrets,
# PostgreSQL and the application. Idempotent: run it again to upgrade. Needs the tunnel
# (tunnel.sh) and the kubeconfig (fetch-kubeconfig.sh). Argo CD takes over this job later on.
#
#   KUBECONFIG=~/.kube/votely-aws.yaml deploy/aws/install.sh                # images tagged main
#   KUBECONFIG=~/.kube/votely-aws.yaml VOTELY_TAG=0.1.0 deploy/aws/install.sh
set -euo pipefail
cd "$(dirname "$0")/../.."

NAMESPACE=votely
TAG=${VOTELY_TAG:-main}
CERT_MANAGER_VERSION=v1.21.2

[ "$(kubectl config current-context)" = votely-aws ] || { echo "Use the votely-aws kubeconfig." >&2; exit 1; }

helm upgrade --install cert-manager cert-manager --repo https://charts.jetstack.io \
  --version "$CERT_MANAGER_VERSION" --namespace cert-manager --create-namespace \
  --set crds.enabled=true --wait
kubectl apply --filename deploy/aws/cluster-issuers.yaml

kubectl create namespace "$NAMESPACE" --dry-run=client --output yaml | kubectl apply --filename -

# Credentials are generated once, inside the cluster only (Sealed Secrets later on).
if ! kubectl --namespace "$NAMESPACE" get secret votely-db >/dev/null 2>&1; then
  kubectl --namespace "$NAMESPACE" create secret generic votely-db \
    --from-literal=username=votely \
    --from-literal=password="$(openssl rand -hex 24)" \
    --from-literal=database=votely
fi
if ! kubectl --namespace "$NAMESPACE" get secret votely-jwt >/dev/null 2>&1; then
  kubectl --namespace "$NAMESPACE" create secret generic votely-jwt \
    --from-literal=jwt-secret="$(openssl rand -hex 32)"
fi

helm upgrade --install postgres deploy/helm/postgres --namespace "$NAMESPACE" --wait
helm upgrade --install votely deploy/helm/votely --namespace "$NAMESPACE" \
  --values deploy/helm/votely/values-aws.yaml --set image.tag="$TAG" --wait

echo "Votely $TAG: https://$(grep '^host:' deploy/helm/votely/values-aws.yaml | cut -d' ' -f2)"
echo "The certificate takes about a minute: kubectl --namespace $NAMESPACE get certificate"
