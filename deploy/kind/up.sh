#!/usr/bin/env bash
# Local Kubernetes environment: kind cluster, Traefik ingress, PostgreSQL and Votely.
# Idempotent: run it again to upgrade. Open http://votely.localhost when it is done.
#
#   deploy/kind/up.sh                     # images tagged `main` (latest verified build)
#   VOTELY_TAG=0.1.0 deploy/kind/up.sh    # a released version
set -euo pipefail
cd "$(dirname "$0")/../.."

CLUSTER=votely
NAMESPACE=votely
TAG=${VOTELY_TAG:-main}
TRAEFIK_CHART_VERSION=41.6.1

if ! kind get clusters | grep -qx "$CLUSTER"; then
  kind create cluster --config deploy/kind/cluster.yaml
fi
kubectl config use-context "kind-$CLUSTER"

helm upgrade --install traefik traefik --repo https://traefik.github.io/charts \
  --version "$TRAEFIK_CHART_VERSION" --namespace traefik --create-namespace \
  --values deploy/kind/traefik-values.yaml --wait

kubectl create namespace "$NAMESPACE" --dry-run=client --output yaml | kubectl apply --filename -

# Credentials are generated once, inside the cluster only: nothing secret is written to disk
# or to Git. On the server, Sealed Secrets provides the same two Secrets.
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

# The database first: the application's migrations run before its pods start.
helm upgrade --install postgres deploy/helm/postgres --namespace "$NAMESPACE" --wait
helm upgrade --install votely deploy/helm/votely --namespace "$NAMESPACE" \
  --values deploy/helm/votely/values-kind.yaml --set image.tag="$TAG" --wait

echo "Votely $TAG is running on http://votely.localhost"
