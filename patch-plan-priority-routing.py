from __future__ import annotations

from pathlib import Path

ROOT = Path("/app/app")


def replace_once(path: Path, text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"{path}: could not apply {label}")


def patch_load_balancer_priority() -> None:
    path = ROOT / "modules/proxy/load_balancer.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "def _state_above_budget_threshold(state: AccountState, budget_threshold_pct: float) -> bool:\n",
        "PLAN_PRIORITY_ALIASES_FOR_STICKY = {\n"
        "    \"pro lite\": \"prolite\",\n"
        "    \"pro-lite\": \"prolite\",\n"
        "    \"pro_lite\": \"prolite\",\n"
        "}\n"
        "PLAN_PRIORITY_GROUPS_FOR_STICKY = {\n"
        "    \"plus\": 0,\n"
        "    \"prolite\": 1,\n"
        "    \"pro\": 1,\n"
        "}\n\n\n"
        "def _plan_priority_group_for_state(state: AccountState) -> int:\n"
        "    normalized = (state.plan_type or \"\").strip().lower()\n"
        "    resolved = PLAN_PRIORITY_ALIASES_FOR_STICKY.get(normalized, normalized)\n"
        "    return PLAN_PRIORITY_GROUPS_FOR_STICKY.get(resolved, 2)\n\n\n"
        "def _priority_preferred_states(states: list[AccountState]) -> list[AccountState]:\n"
        "    if not states:\n"
        "        return []\n"
        "    best_group = min(_plan_priority_group_for_state(state) for state in states)\n"
        "    return [state for state in states if _plan_priority_group_for_state(state) == best_group]\n\n\n"
        "def _higher_priority_available(\n"
        "    states: list[AccountState],\n"
        "    pinned: AccountState,\n"
        "    *,\n"
        "    prefer_earlier_reset: bool,\n"
        "    routing_strategy: RoutingStrategy,\n"
        "    budget_threshold_pct: float,\n"
        ") -> bool:\n"
        "    pinned_group = _plan_priority_group_for_state(pinned)\n"
        "    if pinned_group <= 0:\n"
        "        return False\n"
        "    candidates = [\n"
        "        state\n"
        "        for state in states\n"
        "        if state.account_id != pinned.account_id\n"
        "        and _plan_priority_group_for_state(state) < pinned_group\n"
        "    ]\n"
        "    if not candidates:\n"
        "        return False\n"
        "    budget_safe = [state for state in candidates if not _state_above_budget_threshold(state, budget_threshold_pct)]\n"
        "    candidate_pool = budget_safe or candidates\n"
        "    result = select_account(\n"
        "        candidate_pool,\n"
        "        prefer_earlier_reset=prefer_earlier_reset,\n"
        "        routing_strategy=routing_strategy,\n"
        "        allow_backoff_fallback=False,\n"
        "        deterministic_probe=True,\n"
        "    )\n"
        "    return result.account is not None\n\n\n"
        "def _state_above_budget_threshold(state: AccountState, budget_threshold_pct: float) -> bool:\n",
        "add load balancer plan priority helpers",
    )
    text = replace_once(
        path,
        text,
        "                if not (budget_pressured or rate_limit_far_away):\n",
        "                priority_rebind = _higher_priority_available(\n"
        "                    states,\n"
        "                    pinned,\n"
        "                    prefer_earlier_reset=prefer_earlier_reset_accounts,\n"
        "                    routing_strategy=routing_strategy,\n"
        "                    budget_threshold_pct=budget_threshold_pct,\n"
        "                )\n"
        "                if priority_rebind:\n"
        "                    reallocate_sticky = True\n"
        "                if not (budget_pressured or rate_limit_far_away or priority_rebind):\n",
        "let higher-priority plans rebind sticky mappings",
    )
    text = replace_once(
        path,
        text,
        "    state_list = list(states)\n"
        "    preferred_states = [state for state in state_list if not _state_above_budget_threshold(state, budget_threshold_pct)]\n"
        "    if preferred_states and len(preferred_states) != len(state_list):\n"
        "        preferred = select_account(\n"
        "            preferred_states,\n"
        "            prefer_earlier_reset=prefer_earlier_reset,\n"
        "            routing_strategy=routing_strategy,\n"
        "            allow_backoff_fallback=allow_backoff_fallback,\n"
        "            deterministic_probe=deterministic_probe,\n"
        "        )\n"
        "        if preferred.account is not None:\n"
        "            return preferred\n"
        "    return select_account(\n"
        "        state_list,\n",
        "    state_list = list(states)\n"
        "    priority_states = _priority_preferred_states(state_list)\n"
        "    preferred_states = [\n"
        "        state for state in priority_states if not _state_above_budget_threshold(state, budget_threshold_pct)\n"
        "    ]\n"
        "    if preferred_states and len(preferred_states) != len(priority_states):\n"
        "        preferred = select_account(\n"
        "            preferred_states,\n"
        "            prefer_earlier_reset=prefer_earlier_reset,\n"
        "            routing_strategy=routing_strategy,\n"
        "            allow_backoff_fallback=allow_backoff_fallback,\n"
        "            deterministic_probe=deterministic_probe,\n"
        "        )\n"
        "        if preferred.account is not None:\n"
        "            return preferred\n"
        "    priority_selection = select_account(\n"
        "        priority_states,\n"
        "        prefer_earlier_reset=prefer_earlier_reset,\n"
        "        routing_strategy=routing_strategy,\n"
        "        allow_backoff_fallback=allow_backoff_fallback,\n"
        "        deterministic_probe=deterministic_probe,\n"
        "    )\n"
        "    if priority_selection.account is not None:\n"
        "        return priority_selection\n"
        "    return select_account(\n"
        "        state_list,\n",
        "make plan priority win before budget fallback",
    )
    path.write_text(text)


def main() -> None:
    path = ROOT / "core/balancer/logic.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "def _fallback_secondary_capacity_credits(plan_type: str | None) -> float:\n",
        "PLAN_PRIORITY_ALIASES = {\n"
        "    \"pro lite\": \"prolite\",\n"
        "    \"pro-lite\": \"prolite\",\n"
        "    \"pro_lite\": \"prolite\",\n"
        "}\n"
        "PLAN_PRIORITY_GROUPS = {\n"
        "    \"plus\": 0,\n"
        "    \"prolite\": 1,\n"
        "    \"pro\": 1,\n"
        "}\n\n\n"
        "def _plan_priority_group(state: AccountState) -> int:\n"
        "    normalized = (state.plan_type or \"\").strip().lower()\n"
        "    resolved = PLAN_PRIORITY_ALIASES.get(normalized, normalized)\n"
        "    return PLAN_PRIORITY_GROUPS.get(resolved, 2)\n\n\n"
        "def _prefer_priority_plan_candidates(available: list[AccountState]) -> list[AccountState]:\n"
        "    if not available:\n"
        "        return available\n"
        "    best_group = min(_plan_priority_group(state) for state in available)\n"
        "    return [state for state in available if _plan_priority_group(state) == best_group]\n\n\n"
        "def _fallback_secondary_capacity_credits(plan_type: str | None) -> float:\n",
        "add plan priority helpers",
    )
    text = replace_once(
        path,
        text,
        "    effective_pool = healthy or probing or draining or available\n\n    if routing_strategy == \"round_robin\":\n",
        "    effective_pool = healthy or probing or draining or available\n"
        "    effective_pool = _prefer_priority_plan_candidates(effective_pool)\n\n"
        "    if routing_strategy == \"round_robin\":\n",
        "apply plan priority before strategy",
    )
    path.write_text(text)
    patch_load_balancer_priority()


if __name__ == "__main__":
    main()
