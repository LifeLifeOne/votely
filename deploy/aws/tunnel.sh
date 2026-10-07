#!/usr/bin/env bash
# Forward localhost:6443 to the Kubernetes API of the server through Systems Manager. The API is
# never exposed on the internet. Keep this running while using kubectl; Ctrl+C closes it.
set -euo pipefail

instance=$(aws ec2 describe-instances \
  --filters Name=tag:Name,Values=votely-server Name=instance-state-name,Values=running \
  --query 'Reservations[0].Instances[0].InstanceId' --output text)
[ "$instance" != "None" ] || { echo "No running votely-server instance." >&2; exit 1; }

exec aws ssm start-session --target "$instance" \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["6443"],"localPortNumber":["6443"]}'
