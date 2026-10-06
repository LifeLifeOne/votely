#!/usr/bin/env bash
# Delete the local Kubernetes cluster and everything in it, database included.
set -euo pipefail
kind delete cluster --name votely
