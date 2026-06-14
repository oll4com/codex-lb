# codex-lb

Public OLL4 patch overlay for [Soju06/codex-lb](https://github.com/Soju06/codex-lb).

This repository does not republish the full upstream application source. It contains the
public-safe Docker overlay, patch stack, and verification helpers we use on top of the
upstream `ghcr.io/soju06/codex-lb:latest` image.

## Upstream Origin

- Original upstream repository: `Soju06/codex-lb`
- Upstream image base used here: `ghcr.io/soju06/codex-lb:latest`
- Upstream project license and release history stay with the upstream repository

## What This Repo Contains

- `Dockerfile`: builds the public OLL4 overlay on top of the upstream image
- `patch-*.py`: public-safe patch stack for compatibility, routing, UI, and API behavior
- `upgrade-and-verify.sh`: rebuild/redeploy helper
- `verify-compat.sh`: validation helper after rebuilds/upgrades

## Public-Safe Patch Areas

- model catalog and API compatibility fixes
- dashboard clipboard and live-usage UI improvements
- context overflow and overload/failover handling
- OAuth provider, re-auth, and dialog compatibility fixes
- auto-model and plan-priority routing improvements
- weekly remaining and plan-capacity helper endpoints

## Intentionally Excluded From The Public Export

- `.env` files, `.secrets/`, tokens, passwords, and any private credentials
- runtime SQLite stores, volume archives, and `runtime-state/` snapshots
- account-specific internal routing customizations
- ad-hoc backups and other environment-specific runtime artifacts
