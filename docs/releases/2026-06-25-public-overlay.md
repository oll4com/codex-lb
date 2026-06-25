# Public Overlay Release - 2026-06-25

## Scope

This repository is the public-safe OLL4 overlay for `codex-lb`. It is not a full mirror of the private runtime repository and it intentionally excludes runtime snapshots, databases, secrets, backups, and internal deployment artifacts.

## What changed in this public-source release

The source changes shipped in this release are focused on plan normalization and plan persistence safety:

1. `patch-plan-capacities.py` now recognizes `prolite` aliases consistently across:
   - account plan parsing
   - rate-limit plan parsing
   - balancer capacity aliases
2. `patch-plan-capacities.py` now publishes explicit plan priorities:
   - `free`
   - `plus`
   - `prolite`
   - `pro`
   - `edu`
   - `team`
   - `business`
   - `enterprise`
3. `patch-plan-capacities.py` now exposes `resolve_persisted_account_plan_type(...)` so the overlay can compare a newly observed plan with the already persisted one.
4. `patch-plan-guard.py` applies that helper in the two downgrade-prone paths:
   - account auth refresh
   - usage sync
5. Result: a stale lower-tier observation no longer silently overwrites a higher-tier persisted account plan during refresh/sync cycles.

## Additional OLL4 capabilities now documented in the public repo

The screenshot gallery and notes in this release also document the latest verified OLL4 runtime capabilities that are currently visible on the deployed dashboard:

1. Top 5 API usage and model-usage dashboard cards
2. live account usage strip with privacy-aware redaction and live/recent pills
3. latency panel with signals, model latency, and upstream route observability
4. fixed 5-minute error-rate companion metric next to the native timeframe error metric
5. remaining-credit visualizations for short-window and weekly quota state
6. guarded routing/balancing behavior for account selection and failover
7. weekly remaining/quota helper surfaces for downstream consumers

These capabilities are shown with public-safe redacted screenshots so the public repository reflects the current product state without publishing private runtime internals.

## Public-safety rules followed for this release

The public release intentionally excludes:

- runtime-state trees
- `store.db`, `.db`, `.sqlite`, `.sqlite3`
- secrets, API keys, auth cookies, and `.env` files
- internal service dumps and deployment bundles
- raw screenshots with emails, internal IPs, or unredacted account identifiers

All published screenshots in `docs/screenshots/` were redacted before commit.
