#!/usr/bin/env bash
set -euo pipefail

cd /opt/codex-lb-lab

docker pull ghcr.io/soju06/codex-lb:latest
docker-compose build --pull codex-lb
docker-compose up -d codex-lb
./verify-compat.sh
