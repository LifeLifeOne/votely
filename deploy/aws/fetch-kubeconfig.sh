#!/usr/bin/env bash
# Fetch the k3s admin kubeconfig from the server through Systems Manager (no SSH) and save it
# outside the repository. It targets https://127.0.0.1:6443: the local end of tunnel.sh.
#
#   deploy/aws/fetch-kubeconfig.sh    # writes ~/.kube/votely-aws.yaml (context votely-aws)
set -euo pipefail

KUBECONFIG_FILE="${HOME}/.kube/votely-aws.yaml"
instance=$(aws ec2 describe-instances \
  --filters Name=tag:Name,Values=votely-server Name=instance-state-name,Values=running \
  --query 'Reservations[0].Instances[0].InstanceId' --output text)
[ "$instance" != "None" ] || { echo "No running votely-server instance." >&2; exit 1; }

# The session prints banners around the file: keep the YAML only.
raw=$(aws ssm start-session --target "$instance" \
  --document-name AWS-StartInteractiveCommand \
  --parameters command="sudo cat /etc/rancher/k3s/k3s.yaml")
yaml=$(printf '%s\n' "$raw" | tr -d '\r' | sed -n '/^apiVersion:/,/^Exiting session/p' | sed '/^Exiting session/d')
[ -n "$yaml" ] || { echo "Could not read the kubeconfig from $instance." >&2; exit 1; }

# Name the cluster, user and context "votely-aws" (k3s calls them all "default").
mkdir -p "$(dirname "$KUBECONFIG_FILE")"
umask 077
printf '%s\n' "$yaml" | sed 's/: default$/: votely-aws/' > "$KUBECONFIG_FILE"
echo "Saved $KUBECONFIG_FILE (context votely-aws). Open the tunnel with deploy/aws/tunnel.sh, then:"
echo "  export KUBECONFIG=$KUBECONFIG_FILE && kubectl get nodes"
