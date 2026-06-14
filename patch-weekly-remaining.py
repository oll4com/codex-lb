from pathlib import Path

API_FILE = Path('/app/app/modules/proxy/api.py')


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f'target snippet not found: {label}')
    return content.replace(old, new, 1)

api_content = API_FILE.read_text()

route = '''\n\n@usage_router.get("/api/codex/weekly-remaining")\n@usage_router.get("/api/codex/weekly-remaining/", include_in_schema=False)\nasync def codex_weekly_remaining(\n    api_key: ApiKeyData = Security(validate_usage_api_key),\n) -> JSONResponse:\n    del api_key\n    async with get_background_session() as session:\n        aggregate_limits = await _build_aggregate_credit_limits(session)\n\n    weekly_limit = aggregate_limits.get("7d")\n    if weekly_limit is None:\n        raise ProxyAuthError("Weekly aggregate usage is unavailable")\n\n    capacity_credits = max(0, weekly_limit.max_value)\n    used_credits = max(0, min(weekly_limit.current_value, capacity_credits))\n    remaining_credits = max(0, capacity_credits - used_credits)\n    used_percent = (used_credits / capacity_credits) * 100.0 if capacity_credits else 0.0\n    remaining_percent = max(0.0, 100.0 - used_percent)\n\n    return JSONResponse(\n        content={\n            "object": "codex_lb.weekly_remaining",\n            "window": "7d",\n            "window_key": "secondary",\n            "used_percent": round(used_percent, 2),\n            "remaining_percent": round(remaining_percent, 2),\n            "capacity_credits": capacity_credits,\n            "used_credits": used_credits,\n            "remaining_credits": remaining_credits,\n            "reset_at": weekly_limit.reset_at,\n            "source": weekly_limit.source,\n        }\n    )\n'''

api_content = replace_once(
    api_content,
    '\n\ndef _build_v1_usage_limits(\n',
    route + '\n\ndef _build_v1_usage_limits(\n',
    'weekly remaining route insertion',
)

API_FILE.write_text(api_content)
