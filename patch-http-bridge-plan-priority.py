from __future__ import annotations

from pathlib import Path

ROOT = Path("/app/app")


def replace_once(path: Path, text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"{path}: could not apply {label}")


def patch_service() -> None:
    path = ROOT / "modules/proxy/service.py"
    text = path.read_text()

    text = replace_once(
        path,
        text,
        "logger = logging.getLogger(__name__)\n\n",
        "logger = logging.getLogger(__name__)\n\n"
        "PLAN_PRIORITY_ALIASES_FOR_HTTP_BRIDGE = {\n"
        "    \"pro lite\": \"prolite\",\n"
        "    \"pro-lite\": \"prolite\",\n"
        "    \"pro_lite\": \"prolite\",\n"
        "}\n"
        "PLAN_PRIORITY_GROUPS_FOR_HTTP_BRIDGE = {\n"
        "    \"plus\": 0,\n"
        "    \"prolite\": 1,\n"
        "    \"pro\": 1,\n"
        "}\n\n\n"
        "def _http_bridge_plan_priority_group(plan_type: str | None) -> int:\n"
        "    normalized = (plan_type or \"\").strip().lower()\n"
        "    resolved = PLAN_PRIORITY_ALIASES_FOR_HTTP_BRIDGE.get(normalized, normalized)\n"
        "    return PLAN_PRIORITY_GROUPS_FOR_HTTP_BRIDGE.get(resolved, 2)\n\n\n"
        "def _http_bridge_account_plan_priority_group(account: Account | None) -> int:\n"
        "    if account is None:\n"
        "        return 2\n"
        "    return _http_bridge_plan_priority_group(getattr(account, \"plan_type\", None))\n\n\n",
        "add HTTP bridge plan priority helpers",
    )

    methods = '''    async def _higher_priority_account_available(
        self,
        current_account: Account,
        *,
        api_key: ApiKeyData | None,
        request_model: str | None,
    ) -> bool:
        current_priority = _http_bridge_account_plan_priority_group(current_account)
        if current_priority <= 0:
            return False
        scoped_account_ids = (
            set(api_key.assigned_account_ids)
            if api_key is not None and api_key.account_assignment_scope_enabled
            else None
        )
        settings = await get_settings_cache().get()
        selection = await self._load_balancer.select_account(
            sticky_key=None,
            sticky_kind=None,
            reallocate_sticky=False,
            sticky_max_age_seconds=None,
            prefer_earlier_reset_accounts=settings.prefer_earlier_reset_accounts,
            routing_strategy=_routing_strategy(settings),
            model=request_model,
            account_ids=scoped_account_ids,
            budget_threshold_pct=settings.sticky_reallocation_budget_threshold_pct,
        )
        candidate = selection.account
        if candidate is None or candidate.id == current_account.id:
            return False
        return _http_bridge_account_plan_priority_group(candidate) < current_priority

    async def _http_bridge_session_should_yield_to_plan_priority(
        self,
        session: "_HTTPBridgeSession",
        *,
        api_key: ApiKeyData | None,
        request_model: str | None,
    ) -> bool:
        if session.closed or session.account.status != AccountStatus.ACTIVE:
            return False
        should_yield = await self._higher_priority_account_available(
            session.account,
            api_key=api_key,
            request_model=request_model,
        )
        if should_yield:
            _log_http_bridge_event(
                "priority_rebind",
                session.key,
                account_id=session.account.id,
                model=session.request_model,
                detail="outcome=yield_to_higher_priority_plan",
                cache_key_family=session.key.affinity_kind,
                model_class=_extract_model_class(session.request_model) if session.request_model else None,
            )
        return should_yield

'''
    text = replace_once(
        path,
        text,
        "    async def _create_http_bridge_session_compatible(\n",
        methods + "    async def _create_http_bridge_session_compatible(\n",
        "add HTTP bridge priority methods",
    )

    text = replace_once(
        path,
        text,
        "                            or not _http_bridge_session_matches_preferred_account(\n"
        "                                session=alias_session,\n"
        "                                previous_response_id=previous_response_id,\n"
        "                                preferred_account_id=preferred_account_id,\n"
        "                            )\n",
        "                            or await self._http_bridge_session_should_yield_to_plan_priority(\n"
        "                                alias_session,\n"
        "                                api_key=api_key,\n"
        "                                request_model=request_model,\n"
        "                            )\n"
        "                            or not _http_bridge_session_matches_preferred_account(\n"
        "                                session=alias_session,\n"
        "                                previous_response_id=previous_response_id,\n"
        "                                preferred_account_id=preferred_account_id,\n"
        "                            )\n",
        "make turn-state alias yield to higher priority plan",
    )

    text = replace_once(
        path,
        text,
        "                                and previous_session.account.status == AccountStatus.ACTIVE\n"
        "                                and _http_bridge_session_matches_preferred_account(\n"
        "                                    session=previous_session,\n"
        "                                    previous_response_id=previous_response_id,\n"
        "                                    preferred_account_id=preferred_account_id,\n"
        "                                )\n"
        "                            ):\n",
        "                                and previous_session.account.status == AccountStatus.ACTIVE\n"
        "                                and not await self._http_bridge_session_should_yield_to_plan_priority(\n"
        "                                    previous_session,\n"
        "                                    api_key=api_key,\n"
        "                                    request_model=request_model,\n"
        "                                )\n"
        "                                and _http_bridge_session_matches_preferred_account(\n"
        "                                    session=previous_session,\n"
        "                                    previous_response_id=previous_response_id,\n"
        "                                    preferred_account_id=preferred_account_id,\n"
        "                                )\n"
        "                            ):\n",
        "make previous-response alias yield to higher priority plan",
    )

    text = replace_once(
        path,
        text,
        "                    and _http_bridge_session_matches_preferred_account(\n"
        "                        session=existing,\n"
        "                        previous_response_id=previous_response_id,\n"
        "                        preferred_account_id=preferred_account_id,\n"
        "                    )\n"
        "                ):\n",
        "                    and _http_bridge_session_matches_preferred_account(\n"
        "                        session=existing,\n"
        "                        previous_response_id=previous_response_id,\n"
        "                        preferred_account_id=preferred_account_id,\n"
        "                    )\n"
        "                    and not await self._http_bridge_session_should_yield_to_plan_priority(\n"
        "                        existing,\n"
        "                        api_key=api_key,\n"
        "                        request_model=request_model,\n"
        "                    )\n"
        "                ):\n",
        "make existing bridge session yield to higher priority plan",
    )

    text = replace_once(
        path,
        text,
        "                            if (\n"
        "                                previous_session is not None\n"
        "                                and not previous_session.closed\n"
        "                                and previous_session.account.status == AccountStatus.ACTIVE\n"
        "                            ):\n",
        "                            if (\n"
        "                                previous_session is not None\n"
        "                                and not previous_session.closed\n"
        "                                and previous_session.account.status == AccountStatus.ACTIVE\n"
        "                                and not await self._http_bridge_session_should_yield_to_plan_priority(\n"
        "                                    previous_session,\n"
        "                                    api_key=api_key,\n"
        "                                    request_model=request_model,\n"
        "                                )\n"
        "                            ):\n",
        "make fallback previous-response session yield to higher priority plan",
    )

    text = replace_once(
        path,
        text,
        "                    and _http_bridge_session_matches_preferred_account(\n"
        "                        session=session,\n"
        "                        previous_response_id=previous_response_id,\n"
        "                        preferred_account_id=preferred_account_id,\n"
        "                    )\n"
        "                ):\n",
        "                    and _http_bridge_session_matches_preferred_account(\n"
        "                        session=session,\n"
        "                        previous_response_id=previous_response_id,\n"
        "                        preferred_account_id=preferred_account_id,\n"
        "                    )\n"
        "                    and not await self._http_bridge_session_should_yield_to_plan_priority(\n"
        "                        session,\n"
        "                        api_key=api_key,\n"
        "                        request_model=request_model,\n"
        "                    )\n"
        "                ):\n",
        "make inflight bridge session yield to higher priority plan",
    )

    text = replace_once(
        path,
        text,
        "                _record_continuity_owner_resolution(\n"
        "                    surface=\"http_bridge\",\n"
        "                    source=\"local_bridge_session\",\n"
        "                    outcome=\"hit\",\n"
        "                    previous_response_id=previous_response_id,\n"
        "                    session_id=incoming_turn_state,\n"
        "                )\n"
        "                return session.account.id\n",
        "                if await self._http_bridge_session_should_yield_to_plan_priority(\n"
        "                    session,\n"
        "                    api_key=api_key,\n"
        "                    request_model=None,\n"
        "                ):\n"
        "                    continue\n"
        "                _record_continuity_owner_resolution(\n"
        "                    surface=\"http_bridge\",\n"
        "                    source=\"local_bridge_session\",\n"
        "                    outcome=\"hit\",\n"
        "                    previous_response_id=previous_response_id,\n"
        "                    session_id=incoming_turn_state,\n"
        "                )\n"
        "                return session.account.id\n",
        "make local owner resolution yield to higher priority plan",
    )

    text = replace_once(
        path,
        text,
        "                    if preferred_selection.account is not None:\n"
        "                        logger.info(\n"
        "                            \"Selected preferred account request_id=%s kind=%s request_stage=%s account_id=%s\",\n"
        "                            request_id,\n"
        "                            kind,\n"
        "                            request_stage,\n"
        "                            preferred_account_id,\n"
        "                        )\n"
        "                        return preferred_selection\n",
        "                    if preferred_selection.account is not None:\n"
        "                        if await self._higher_priority_account_available(\n"
        "                            preferred_selection.account,\n"
        "                            api_key=api_key,\n"
        "                            request_model=model,\n"
        "                        ):\n"
        "                            logger.info(\n"
        "                                \"Ignoring lower-priority preferred account request_id=%s kind=%s request_stage=%s account_id=%s\",\n"
        "                                request_id,\n"
        "                                kind,\n"
        "                                request_stage,\n"
        "                                preferred_account_id,\n"
        "                            )\n"
        "                        else:\n"
        "                            logger.info(\n"
        "                                \"Selected preferred account request_id=%s kind=%s request_stage=%s account_id=%s\",\n"
        "                                request_id,\n"
        "                                kind,\n"
        "                                request_stage,\n"
        "                                preferred_account_id,\n"
        "                            )\n"
        "                            return preferred_selection\n",
        "let higher priority plan override preferred account",
    )

    text = replace_once(
        path,
        text,
        "            if require_preferred_account and preferred_account_id is not None and account.id != preferred_account_id:\n",
        "            if (\n"
        "                require_preferred_account\n"
        "                and preferred_account_id is not None\n"
        "                and account.id != preferred_account_id\n"
        "                and _http_bridge_account_plan_priority_group(account) > 0\n"
        "            ):\n",
        "allow Plus to override previous-response owner requirement",
    )

    path.write_text(text)


def main() -> None:
    patch_service()


if __name__ == "__main__":
    main()
