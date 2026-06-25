from __future__ import annotations

from pathlib import Path


ROOT = Path("/app/app")


def replace_once(path: Path, text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"{path}: could not apply {label}")


def patch_auth_manager() -> None:
    path = ROOT / "modules/accounts/auth_manager.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "from app.core.plan_types import coerce_account_plan_type\n",
        "from app.core.plan_types import coerce_account_plan_type, resolve_persisted_account_plan_type\n",
        "import persisted plan helper",
    )
    text = replace_once(
        path,
        text,
        "        if result.plan_type is not None:\n"
        "            account.plan_type = coerce_account_plan_type(\n"
        "                result.plan_type,\n"
        "                account.plan_type or DEFAULT_PLAN,\n"
        "            )\n"
        "        elif not account.plan_type:\n"
        "            account.plan_type = DEFAULT_PLAN\n",
        "        if result.plan_type is not None:\n"
        "            observed_plan_type = coerce_account_plan_type(\n"
        "                result.plan_type,\n"
        "                account.plan_type or DEFAULT_PLAN,\n"
        "            )\n"
        "            next_plan_type = (\n"
        "                resolve_persisted_account_plan_type(account.plan_type or DEFAULT_PLAN, observed_plan_type)\n"
        "                or DEFAULT_PLAN\n"
        "            )\n"
        "            if observed_plan_type != next_plan_type:\n"
        "                logger.info(\n"
        "                    \"Ignoring lower plan from token refresh account_id=%s current=%s observed=%s\",\n"
        "                    account.id,\n"
        "                    account.plan_type,\n"
        "                    observed_plan_type,\n"
        "                )\n"
        "            account.plan_type = next_plan_type\n"
        "        elif not account.plan_type:\n"
        "            account.plan_type = DEFAULT_PLAN\n",
        "guard against stale plan downgrade on refresh",
    )
    path.write_text(text)


def patch_usage_updater() -> None:
    path = ROOT / "modules/usage/updater.py"
    text = path.read_text()
    text = replace_once(
        path,
        text,
        "from app.core.plan_types import coerce_account_plan_type\n",
        "from app.core.plan_types import coerce_account_plan_type, resolve_persisted_account_plan_type\n",
        "import persisted plan helper",
    )
    text = replace_once(
        path,
        text,
        "    async def _sync_plan_type(self, account: Account, payload: UsagePayload) -> None:\n"
        "        next_plan_type = coerce_account_plan_type(payload.plan_type, account.plan_type or \"free\")\n"
        "        if next_plan_type == account.plan_type:\n"
        "            return\n"
        "\n"
        "        account.plan_type = next_plan_type\n"
        "        if not self._auth_manager:\n"
        "            return\n"
        "\n"
        "        await self._auth_manager._repo.update_tokens(\n",
        "    async def _sync_plan_type(self, account: Account, payload: UsagePayload) -> None:\n"
        "        observed_plan_type = coerce_account_plan_type(payload.plan_type, account.plan_type or \"free\")\n"
        "        next_plan_type = resolve_persisted_account_plan_type(account.plan_type, observed_plan_type)\n"
        "        if next_plan_type == account.plan_type:\n"
        "            if observed_plan_type is not None and observed_plan_type != next_plan_type:\n"
        "                logger.info(\n"
        "                    \"Ignoring lower plan from usage sync account_id=%s current=%s observed=%s\",\n"
        "                    account.id,\n"
        "                    account.plan_type,\n"
        "                    observed_plan_type,\n"
        "                )\n"
        "            return\n"
        "\n"
        "        account.plan_type = next_plan_type\n"
        "        if not self._auth_manager:\n"
        "            return\n"
        "\n"
        "        await self._auth_manager._repo.update_tokens(\n",
        "guard against stale plan downgrade on usage sync",
    )
    path.write_text(text)


def main() -> None:
    patch_auth_manager()
    patch_usage_updater()


if __name__ == "__main__":
    main()
