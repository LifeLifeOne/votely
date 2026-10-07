#!/usr/bin/env bash
# Generate the credentials of an environment and seal them, so they can be committed to Git.
# The plain values only exist in this pipe: they are never written to disk or printed.
#
#   deploy/aws/seal-secrets.sh staging   # writes deploy/environments/staging/sealed-secrets.yaml
#
# Sealing uses the controller's public certificate (committed next to this script's output);
# only the controller in the cluster can decrypt. A sealed secret is bound to its namespace and
# name: the staging one cannot be used in production.
set -euo pipefail
cd "$(dirname "$0")/../.."

ENVIRONMENT=${1:?usage: seal-secrets.sh <staging|prod>}
NAMESPACE="votely-$ENVIRONMENT"
CERT=deploy/platform/sealed-secrets/sealing-cert.pem
OUT="deploy/environments/$ENVIRONMENT/sealed-secrets.yaml"

# The public certificate is fetched once from the cluster (tunnel needed), then committed.
if [ ! -f "$CERT" ]; then
  mkdir -p "$(dirname "$CERT")"
  kubeseal --fetch-cert > "$CERT"
  echo "Fetched $CERT: commit it, it is public."
fi
# Rotating credentials is deliberate: remove the file first.
[ ! -f "$OUT" ] || { echo "$OUT already exists. Delete it to generate new credentials." >&2; exit 1; }

seal() { kubeseal --cert "$CERT" --format yaml; }
mkdir -p "$(dirname "$OUT")"
{
  kubectl create secret generic votely-db --namespace "$NAMESPACE" --dry-run=client --output yaml \
    --from-literal=username=votely \
    --from-literal=password="$(openssl rand -hex 24)" \
    --from-literal=database=votely | seal
  echo "---"
  kubectl create secret generic votely-jwt --namespace "$NAMESPACE" --dry-run=client --output yaml \
    --from-literal=jwt-secret="$(openssl rand -hex 32)" | seal
} > "$OUT"
echo "Sealed votely-db and votely-jwt for $NAMESPACE in $OUT"
