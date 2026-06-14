# codex-lb

Public-safe OLL4 Docker overlay for [Soju06/codex-lb](https://github.com/Soju06/codex-lb).

This repository does not republish the full upstream application source. It keeps the OLL4-specific overlay, patch stack, and verification helpers that we apply on top of the upstream `ghcr.io/soju06/codex-lb:latest` image.

## Upstream Attribution

- Original upstream repository: `Soju06/codex-lb`
- Upstream image base used here: `ghcr.io/soju06/codex-lb:latest`
- Upstream project license remains with the upstream repository

## What OLL4 Changed

- compatibility fixes for the OpenAI-compatible API surface
- dashboard UX improvements such as clipboard and live-usage handling
- route-selection, auto-model, and failover behavior patches
- helper endpoints for plan capacity, weekly remaining, and live account usage

## What This Repo Contains

- `Dockerfile` for building the OLL4 overlay on top of the upstream image
- `patch-*.py` scripts for public-safe runtime modifications
- `upgrade-and-verify.sh` for rebuild and redeploy verification
- `verify-compat.sh` for post-upgrade smoke validation

## Intentionally Excluded

- `.env` files, private credentials, and tokens
- runtime SQLite stores, backups, and environment snapshots
- account-specific internal routing customizations
- ad-hoc operational artifacts that do not belong in a public source repo

## License

The overlay files in this repository are released under the MIT License. See [LICENSE](LICENSE).
