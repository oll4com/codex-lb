from __future__ import annotations

from pathlib import Path


ROOT = Path("/app/app")


def replace_once(path: Path, text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"{path}: could not apply {label}")


def patch_plan_types() -> None:
    path = ROOT / "core/plan_types.py"
    text = path.read_text()

    text = replace_once(
        path,
        text,
        '    "plus",\n    "pro",\n',
        '    "plus",\n    "prolite",\n    "pro",\n',
        "add prolite account plan",
    )
    text = replace_once(
        path,
        text,
        '}\n\n\ndef _clean_plan_type',
        '}\n\nACCOUNT_PLAN_ALIASES: Final[dict[str, str]] = {\n'
        '    "pro lite": "prolite",\n'
        '    "pro-lite": "prolite",\n'
        '    "pro_lite": "prolite",\n'
        '}\n\n\ndef _clean_plan_type',
        "add account plan aliases",
    )
    text = replace_once(
        path,
        text,
        "    normalized = cleaned.lower()\n    return normalized if normalized in ACCOUNT_PLAN_TYPES else None\n",
        "    normalized = ACCOUNT_PLAN_ALIASES.get(cleaned.lower(), cleaned.lower())\n"
        "    return normalized if normalized in ACCOUNT_PLAN_TYPES else None\n",
        "normalize account aliases",
    )
    text = replace_once(
        path,
        text,
        "    normalized = cleaned.lower()\n    if normalized in ACCOUNT_PLAN_TYPES:\n",
        "    normalized = ACCOUNT_PLAN_ALIASES.get(cleaned.lower(), cleaned.lower())\n"
        "    if normalized in ACCOUNT_PLAN_TYPES:\n",
        "canonicalize account aliases",
    )
    text = replace_once(
        path,
        text,
        "    normalized = cleaned.lower()\n    return normalized if normalized in RATE_LIMIT_PLAN_TYPES else None\n",
        "    normalized = ACCOUNT_PLAN_ALIASES.get(cleaned.lower(), cleaned.lower())\n"
        "    return normalized if normalized in RATE_LIMIT_PLAN_TYPES else None\n",
        "normalize rate limit aliases",
    )

    path.write_text(text)


def patch_usage_capacities() -> None:
    path = ROOT / "core/usage/__init__.py"
    text = path.read_text()

    text = replace_once(
        path,
        text,
        '    "plus": 225.0,\n    "business": 225.0,\n',
        '    "plus": 225.0,\n    "prolite": 1125.0,\n    "business": 225.0,\n',
        "add prolite primary capacity",
    )
    text = replace_once(
        path,
        text,
        '    "pro": 1500.0,\n',
        '    "pro": 4500.0,\n',
        "set pro primary capacity to plus x20",
    )
    text = replace_once(
        path,
        text,
        '    "plus": 7560.0,\n    "business": 7560.0,\n',
        '    "plus": 7560.0,\n    "prolite": 37800.0,\n    "business": 7560.0,\n',
        "add prolite secondary capacity",
    )
    text = replace_once(
        path,
        text,
        '    "pro": 50400.0,\n',
        '    "pro": 151200.0,\n',
        "set pro secondary capacity to plus x20",
    )

    path.write_text(text)


def patch_balancer_aliases() -> None:
    path = ROOT / "core/balancer/logic.py"
    text = path.read_text()

    text = replace_once(
        path,
        text,
        'CAPACITY_PLAN_ALIASES = {\n    "education": "edu",\n',
        'CAPACITY_PLAN_ALIASES = {\n'
        '    "pro lite": "prolite",\n'
        '    "pro-lite": "prolite",\n'
        '    "pro_lite": "prolite",\n'
        '    "education": "edu",\n',
        "add prolite capacity aliases",
    )

    path.write_text(text)


def main() -> None:
    patch_plan_types()
    patch_usage_capacities()
    patch_balancer_aliases()


if __name__ == "__main__":
    main()
