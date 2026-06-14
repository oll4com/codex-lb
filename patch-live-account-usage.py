from __future__ import annotations

from pathlib import Path

ROOT = Path("/app/app")


def replace_once(path: Path, text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"{path}: could not apply {label}")


def patch_live_usage_module() -> None:
    path = ROOT / "modules/proxy/live_usage.py"
    path.write_text("""from __future__ import annotations\n\nimport time\nfrom dataclasses import dataclass\nfrom datetime import datetime, timezone\nfrom threading import Lock\nfrom uuid import uuid4\n\n\n_RECENT_SELECTION_SECONDS = 20.0\n\n\n@dataclass(frozen=True, slots=True)\nclass LiveUsageToken:\n    account_id: str\n    token_id: str\n\n\n@dataclass(frozen=True, slots=True)\nclass LiveAccountUsageSnapshot:\n    account_id: str\n    active_request_count: int\n    last_selected_at: datetime | None\n    last_live_started_at: datetime | None\n    live_request_id: str | None\n    live_model: str | None\n    live_transport: str | None\n    recently_selected: bool\n\n\n@dataclass(slots=True)\nclass _LiveAccountUsageState:\n    active_tokens: set[str]\n    last_selected_monotonic: float | None = None\n    last_selected_at: datetime | None = None\n    last_live_started_at: datetime | None = None\n    live_request_id: str | None = None\n    live_model: str | None = None\n    live_transport: str | None = None\n\n\n_lock = Lock()\n_state: dict[str, _LiveAccountUsageState] = {}\n\n\ndef _now_utc() -> datetime:\n    return datetime.now(timezone.utc)\n\n\ndef _state_for(account_id: str) -> _LiveAccountUsageState:\n    state = _state.get(account_id)\n    if state is None:\n        state = _LiveAccountUsageState(active_tokens=set())\n        _state[account_id] = state\n    return state\n\n\ndef mark_account_selected(\n    account_id: str,\n    *,\n    request_id: str | None = None,\n    model: str | None = None,\n    transport: str | None = None,\n) -> None:\n    selected_at = _now_utc()\n    with _lock:\n        state = _state_for(account_id)\n        state.last_selected_monotonic = time.monotonic()\n        state.last_selected_at = selected_at\n        if request_id is not None:\n            state.live_request_id = request_id\n        if model is not None:\n            state.live_model = model\n        if transport is not None:\n            state.live_transport = transport\n\n\ndef start_account_usage(\n    account_id: str,\n    *,\n    request_id: str | None = None,\n    model: str | None = None,\n    transport: str | None = None,\n) -> LiveUsageToken:\n    token = LiveUsageToken(account_id=account_id, token_id=uuid4().hex)\n    started_at = _now_utc()\n    with _lock:\n        state = _state_for(account_id)\n        state.active_tokens.add(token.token_id)\n        state.last_selected_monotonic = time.monotonic()\n        state.last_selected_at = started_at\n        state.last_live_started_at = started_at\n        state.live_request_id = request_id\n        state.live_model = model\n        state.live_transport = transport\n    return token\n\n\ndef finish_account_usage(token: LiveUsageToken | None) -> None:\n    if token is None:\n        return\n    with _lock:\n        state = _state.get(token.account_id)\n        if state is None:\n            return\n        state.active_tokens.discard(token.token_id)\n\n\ndef get_live_account_usage_snapshot() -> dict[str, LiveAccountUsageSnapshot]:\n    now = time.monotonic()\n    with _lock:\n        return {\n            account_id: LiveAccountUsageSnapshot(\n                account_id=account_id,\n                active_request_count=len(state.active_tokens),\n                last_selected_at=state.last_selected_at,\n                last_live_started_at=state.last_live_started_at,\n                live_request_id=state.live_request_id,\n                live_model=state.live_model,\n                live_transport=state.live_transport,\n                recently_selected=(\n                    state.last_selected_monotonic is not None\n                    and now - state.last_selected_monotonic <= _RECENT_SELECTION_SECONDS\n                ),\n            )\n            for account_id, state in _state.items()\n        }\n""")


def patch_service() -> None:
    path = ROOT / "modules/proxy/service.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "from app.modules.proxy.load_balancer import AccountSelection, LoadBalancer\n",
        "from app.modules.proxy.load_balancer import AccountSelection, LoadBalancer\n"
        "from app.modules.proxy.live_usage import finish_account_usage, mark_account_selected, start_account_usage\n",
        "import live usage helpers",
    )
    text = replace_once(
        path,
        text,
        "        response_create_lease = AdmissionLease(None)\n\n        try:\n",
        "        response_create_lease = AdmissionLease(None)\n"
        "        live_usage_token = start_account_usage(\n"
        "            account_id_value,\n"
        "            request_id=request_id,\n"
        "            model=model,\n"
        "            transport=request_transport,\n"
        "        )\n\n"
        "        try:\n",
        "start live stream usage tracking",
    )
    text = replace_once(
        path,
        text,
        "        finally:\n            response_create_lease.release()\n",
        "        finally:\n            finish_account_usage(live_usage_token)\n            response_create_lease.release()\n",
        "finish live stream usage tracking",
    )
    text = replace_once(
        path,
        text,
        "                create_lease = await self._get_work_admission().acquire_response_create(compact=True)\n                try:\n                    return await core_compact_responses(payload, filtered, access_token, account_id)\n                finally:\n                    create_lease.release()\n                    pop_compact_timeout_overrides(timeout_tokens)\n",
        "                create_lease = await self._get_work_admission().acquire_response_create(compact=True)\n"
        "                live_usage_token = start_account_usage(\n"
        "                    target.id,\n"
        "                    request_id=request_id,\n"
        "                    model=payload.model,\n"
        "                    transport=_REQUEST_TRANSPORT_HTTP,\n"
        "                )\n"
        "                try:\n"
        "                    return await core_compact_responses(payload, filtered, access_token, account_id)\n"
        "                finally:\n"
        "                    finish_account_usage(live_usage_token)\n"
        "                    create_lease.release()\n"
        "                    pop_compact_timeout_overrides(timeout_tokens)\n",
        "track compact upstream usage",
    )
    text = replace_once(
        path,
        text,
        "                try:\n                    return await core_transcribe_audio(\n",
        "                live_usage_token = start_account_usage(\n"
        "                    target.id,\n"
        "                    request_id=request_id,\n"
        "                    model=transcribe_model,\n"
        "                    transport=_REQUEST_TRANSPORT_HTTP,\n"
        "                )\n"
        "                try:\n"
        "                    return await core_transcribe_audio(\n",
        "start transcribe live usage tracking",
    )
    text = replace_once(
        path,
        text,
        "                finally:\n                    pop_transcribe_timeout_overrides(timeout_tokens)\n",
        "                finally:\n                    finish_account_usage(live_usage_token)\n                    pop_transcribe_timeout_overrides(timeout_tokens)\n",
        "finish transcribe live usage tracking",
    )
    text = replace_once(
        path,
        text,
        "                if selection.account is not None and selection.account.id in excluded_account_ids_set:\n",
        "                if selection.account is not None:\n"
        "                    mark_account_selected(\n"
        "                        selection.account.id,\n"
        "                        request_id=request_id,\n"
        "                        model=model,\n"
        "                        transport=kind,\n"
        "                    )\n"
        "                if selection.account is not None and selection.account.id in excluded_account_ids_set:\n",
        "mark selected accounts for dashboard",
    )
    path.write_text(text)


def patch_account_schemas() -> None:
    path = ROOT / "modules/accounts/schemas.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "    auth: AccountAuthStatus | None = None\n",
        "    auth: AccountAuthStatus | None = None\n"
        "    active_request_count: int = 0\n"
        "    recently_selected: bool = False\n"
        "    last_selected_at: datetime | None = None\n"
        "    last_live_started_at: datetime | None = None\n"
        "    live_request_id: str | None = None\n"
        "    live_model: str | None = None\n"
        "    live_transport: str | None = None\n",
        "add live usage fields",
    )
    path.write_text(text)


def patch_account_mappers() -> None:
    path = ROOT / "modules/accounts/mappers.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "from app.modules.accounts.schemas import (\n",
        "from app.modules.accounts.schemas import (\n",
        "noop import anchor",
    )
    text = replace_once(
        path,
        text,
        "from app.modules.accounts.schemas import (\n",
        "from app.modules.accounts.schemas import (\n",
        "noop import anchor 2",
    )
    if "from app.modules.proxy.live_usage import get_live_account_usage_snapshot\n" not in text:
        text = text.replace(
            "from app.modules.accounts.schemas import (\n",
            "from app.modules.accounts.schemas import (\n",
            1,
        )
        text = text.replace(
            "from app.modules.accounts.schemas import (\n",
            "from app.modules.accounts.schemas import (\n",
            1,
        )
        marker = "from app.modules.accounts.schemas import (\n"
        idx = text.find(marker)
        if idx == -1:
            raise RuntimeError(f"{path}: import marker not found")
        # Insert after the schemas import block to avoid circular-looking grouping.
        end = text.find("\n)\n", idx)
        if end == -1:
            raise RuntimeError(f"{path}: schemas import block end not found")
        end += len("\n)\n")
        text = text[:end] + "from app.modules.proxy.live_usage import get_live_account_usage_snapshot\n" + text[end:]
    text = replace_once(
        path,
        text,
        "    return [\n        _account_to_summary(\n",
        "    live_usage_by_account = get_live_account_usage_snapshot()\n    return [\n        _account_to_summary(\n",
        "load live usage snapshot once",
    )
    text = replace_once(
        path,
        text,
        "            include_auth=include_auth,\n        )\n",
        "            include_auth=include_auth,\n            live_usage=live_usage_by_account.get(account.id),\n        )\n",
        "pass live usage snapshot",
    )
    text = replace_once(
        path,
        text,
        "    include_auth: bool = True,\n) -> AccountSummary:\n",
        "    include_auth: bool = True,\n    live_usage=None,\n) -> AccountSummary:\n",
        "accept live usage snapshot",
    )
    text = replace_once(
        path,
        text,
        "        auth=auth_status,\n    )\n",
        "        auth=auth_status,\n"
        "        active_request_count=live_usage.active_request_count if live_usage else 0,\n"
        "        recently_selected=live_usage.recently_selected if live_usage else False,\n"
        "        last_selected_at=live_usage.last_selected_at if live_usage else None,\n"
        "        last_live_started_at=live_usage.last_live_started_at if live_usage else None,\n"
        "        live_request_id=live_usage.live_request_id if live_usage else None,\n"
        "        live_model=live_usage.live_model if live_usage else None,\n"
        "        live_transport=live_usage.live_transport if live_usage else None,\n"
        "    )\n",
        "include live usage fields",
    )
    path.write_text(text)


def patch_dashboard_recent_activity() -> None:
    path = ROOT / "modules/dashboard/service.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "        account_summaries = build_account_summaries(\n"
        "            accounts=accounts,\n"
        "            primary_usage=primary_usage,\n"
        "            secondary_usage=secondary_usage,\n"
        "            encryptor=self._encryptor,\n"
        "            include_auth=False,\n"
        "        )\n",
        "        account_summaries = build_account_summaries(\n"
        "            accounts=accounts,\n"
        "            primary_usage=primary_usage,\n"
        "            secondary_usage=secondary_usage,\n"
        "            encryptor=self._encryptor,\n"
        "            include_auth=False,\n"
        "        )\n"
        "        recent_live_logs = await self._repo.list_logs_since(now - timedelta(seconds=60))\n"
        "        _apply_recent_live_account_activity(account_summaries, recent_live_logs)\n",
        "apply recent request-log account activity",
    )
    helper = '''\n\ndef _apply_recent_live_account_activity(account_summaries, recent_logs) -> None:\n    latest_by_account = {}\n    for log in recent_logs:\n        account_id = getattr(log, "account_id", None)\n        if not account_id:\n            continue\n        existing = latest_by_account.get(account_id)\n        if existing is None or getattr(log, "requested_at", None) > getattr(existing, "requested_at", None):\n            latest_by_account[account_id] = log\n\n    for summary in account_summaries:\n        log = latest_by_account.get(summary.account_id)\n        if log is None:\n            continue\n        summary.recently_selected = True\n        summary.last_selected_at = getattr(log, "requested_at", None)\n        if not summary.last_live_started_at:\n            summary.last_live_started_at = getattr(log, "requested_at", None)\n        summary.live_request_id = getattr(log, "request_id", None)\n        summary.live_model = getattr(log, "model", None)\n        summary.live_transport = getattr(log, "transport", None)\n'''
    if "def _apply_recent_live_account_activity(" not in text:
        text += helper
    path.write_text(text)


def main() -> None:
    patch_live_usage_module()
    patch_service()
    patch_account_schemas()
    patch_account_mappers()
    patch_dashboard_recent_activity()


if __name__ == "__main__":
    main()
