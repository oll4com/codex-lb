from pathlib import Path


API_FILE = Path("/app/app/modules/proxy/api.py")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"target snippet not found: {label}")
    return content.replace(old, new, 1)


api_content = API_FILE.read_text()

api_content = replace_once(
    api_content,
    "from app.core.openai.requests import ResponsesCompactRequest, ResponsesRequest\n",
    "from app.core.openai.requests import ResponsesCompactRequest, ResponsesReasoning, ResponsesRequest\n",
    "import ResponsesReasoning",
)

api_content = replace_once(
    api_content,
    "from app.core.utils.json_guards import is_json_mapping\n",
    "from app.core.utils.json_guards import is_json_mapping\nfrom app.core.utils.request_id import get_request_id\n",
    "import get_request_id",
)

api_content = replace_once(
    api_content,
    '_TRANSCRIPTION_MODEL = "gpt-4o-transcribe"\n',
    '_TRANSCRIPTION_MODEL = "gpt-4o-transcribe"\n_AUTO_MODEL_SLUG = "auto"\n',
    "auto model constant",
)

api_content = replace_once(
    api_content,
    """    entries: list[CodexModelEntry] = []
    for slug, model in models.items():
        if not is_public_model(model, allowed_models):
            continue
        entries.append(_to_codex_model_entry(model))
""",
    """    entries: list[CodexModelEntry] = []
    eligible_models = [model for model in models.values() if is_public_model(model, allowed_models)]
    if eligible_models:
        entries.append(_build_auto_codex_model_entry(eligible_models))
    for model in eligible_models:
        entries.append(_to_codex_model_entry(model))
""",
    "backend codex model entries include auto",
)

api_content = replace_once(
    api_content,
    """    items: list[ModelListItem] = []
    for slug, model in models.items():
        if not is_public_model(model, allowed_models):
            continue
        items.append(
            ModelListItem(
                id=slug,
                created=created,
                owned_by="codex-lb",
                metadata=_to_model_metadata(model),
            )
        )
""",
    """    items: list[ModelListItem] = []
    eligible_models = [model for model in models.values() if is_public_model(model, allowed_models)]
    if eligible_models:
        items.append(_build_auto_model_list_item(eligible_models, created))
    for model in eligible_models:
        items.append(
            ModelListItem(
                id=model.slug,
                created=created,
                owned_by="codex-lb",
                metadata=_to_model_metadata(model),
            )
        )
""",
    "openai model entries include auto",
)

api_content = replace_once(
    api_content,
    """    items: list[ModelListItem] = []
    codex_entries: list[CodexModelEntry] = []
    for slug, model in models.items():
        if not is_public_model(model, allowed_models):
            continue
        items.append(
            ModelListItem(
                id=slug,
                created=created,
                owned_by="codex-lb",
                metadata=_to_model_metadata(model),
            )
        )
        codex_entries.append(_to_codex_model_entry(model))
    return items, codex_entries
""",
    """    items: list[ModelListItem] = []
    codex_entries: list[CodexModelEntry] = []
    eligible_models = [model for model in models.values() if is_public_model(model, allowed_models)]
    if eligible_models:
        items.append(_build_auto_model_list_item(eligible_models, created))
        codex_entries.append(_build_auto_codex_model_entry(eligible_models))
    for model in eligible_models:
        items.append(
            ModelListItem(
                id=model.slug,
                created=created,
                owned_by="codex-lb",
                metadata=_to_model_metadata(model),
            )
        )
        codex_entries.append(_to_codex_model_entry(model))
    return items, codex_entries
""",
    "combined model entries include auto",
)

api_content = replace_once(
    api_content,
    """def _to_codex_model_entry(model: UpstreamModel) -> CodexModelEntry:
""",
    """def _build_auto_reasoning_levels() -> list[ReasoningLevelSchema]:
    return [
        ReasoningLevelSchema(effort="low", description="Auto-selected quick reasoning"),
        ReasoningLevelSchema(effort="medium", description="Auto-selected balanced reasoning"),
        ReasoningLevelSchema(effort="high", description="Auto-selected deep reasoning"),
    ]


def _auto_context_window(models: list[UpstreamModel]) -> int:
    windows = [_effective_context_window(model) for model in models if _effective_context_window(model) > 0]
    return max(windows) if windows else 0


def _auto_compact_token_limit(models: list[UpstreamModel]) -> int | None:
    raw_limits: list[int] = []
    for model in models:
        raw_limit = model.raw.get("auto_compact_token_limit")
        if isinstance(raw_limit, int) and raw_limit > 0:
            raw_limits.append(raw_limit)
    if raw_limits:
        return max(raw_limits)

    # Keep Codex stock auto-compaction enabled for the synthetic Auto model.
    # Leave enough headroom for ChatGPT bridge/session-header overhead.
    context_window = _auto_context_window(models)
    if context_window <= 0:
        return None
    return max(16000, min(context_window - 32000, int(context_window * 0.70)))


def _build_auto_model_metadata(models: list[UpstreamModel]) -> ModelMetadata:
    return ModelMetadata(
        display_name="Auto",
        description="Codex LB chooses the best available model and reasoning effort per request.",
        context_window=_auto_context_window(models),
        input_modalities=sorted({modality for model in models for modality in model.input_modalities}) or ["text"],
        supported_reasoning_levels=_build_auto_reasoning_levels(),
        default_reasoning_level=None,
        supports_reasoning_summaries=any(model.supports_reasoning_summaries for model in models),
        support_verbosity=any(model.support_verbosity for model in models),
        default_verbosity=None,
        prefer_websockets=any(model.prefer_websockets for model in models),
        supports_parallel_tool_calls=any(model.supports_parallel_tool_calls for model in models),
        supported_in_api=True,
        minimal_client_version=None,
        priority=max((model.priority for model in models), default=0) + 1000,
    )


def _build_auto_model_list_item(models: list[UpstreamModel], created: int) -> ModelListItem:
    return ModelListItem(
        id=_AUTO_MODEL_SLUG,
        created=created,
        owned_by="codex-lb",
        metadata=_build_auto_model_metadata(models),
    )


def _auto_codex_extra_fields(models: list[UpstreamModel]) -> dict[str, JsonValue]:
    skip_keys = {
        "slug",
        "display_name",
        "description",
        "base_instructions",
        "default_reasoning_level",
        "supported_reasoning_levels",
        "supported_in_api",
        "priority",
        "minimal_client_version",
        "supports_reasoning_summaries",
        "support_verbosity",
        "default_verbosity",
        "supports_parallel_tool_calls",
        "context_window",
        "input_modalities",
        "available_in_plans",
        "prefer_websockets",
        "visibility",
    }
    template = sorted(models, key=lambda model: (model.priority, model.slug))[0]
    extra = {
        key: value
        for key, value in template.raw.items()
        if key not in skip_keys and isinstance(value, (bool, int, float, str, type(None), list, Mapping))
    }
    extra.setdefault("apply_patch_tool_type", "freeform")
    extra.setdefault("web_search_tool_type", "text")
    extra.setdefault("supports_image_detail_original", True)
    extra.setdefault("truncation_policy", {"mode": "tokens", "limit": 10000})
    extra.setdefault("max_context_window", _auto_context_window(models))
    if extra.get("auto_compact_token_limit") is None:
        extra["auto_compact_token_limit"] = _auto_compact_token_limit(models)
    extra.setdefault("reasoning_summary_format", "experimental")
    extra.setdefault("default_reasoning_summary", "none")
    extra.setdefault("shell_type", "shell_command")
    extra.setdefault("availability_nux", None)
    extra.setdefault("upgrade", None)
    extra.setdefault("experimental_supported_tools", [])
    extra.setdefault("supports_search_tool", True)
    extra.setdefault("service_tiers", [])
    extra.setdefault("additional_speed_tiers", [])
    return extra


def _build_auto_codex_model_entry(models: list[UpstreamModel]) -> CodexModelEntry:
    return CodexModelEntry(
        slug=_AUTO_MODEL_SLUG,
        display_name="Auto",
        description="Codex LB chooses the best available model and reasoning effort per request.",
        base_instructions="",
        default_reasoning_level=None,
        supported_reasoning_levels=_build_auto_reasoning_levels(),
        supported_in_api=True,
        priority=max((model.priority for model in models), default=0) + 1000,
        minimal_client_version=None,
        supports_reasoning_summaries=any(model.supports_reasoning_summaries for model in models),
        support_verbosity=any(model.support_verbosity for model in models),
        default_verbosity=None,
        supports_parallel_tool_calls=any(model.supports_parallel_tool_calls for model in models),
        context_window=_auto_context_window(models),
        input_modalities=sorted({modality for model in models for modality in model.input_modalities}) or ["text"],
        available_in_plans=sorted({plan for model in models for plan in model.available_in_plans}),
        prefer_websockets=any(model.prefer_websockets for model in models),
        visibility="list",
        **_auto_codex_extra_fields(models),
    )


def _to_codex_model_entry(model: UpstreamModel) -> CodexModelEntry:
""",
    "auto model entry helpers",
)

api_content = replace_once(
    api_content,
    """    effective_model = _effective_model_for_api_key(api_key, payload.model)
    validate_model_access(api_key, effective_model)

    rate_limit_headers = await context.service.rate_limit_headers()
    try:
        responses_payload = payload.to_responses_request()
""",
    """    effective_model = _effective_model_for_api_key(api_key, payload.model)
    if effective_model != _AUTO_MODEL_SLUG:
        validate_model_access(api_key, effective_model)

    rate_limit_headers = await context.service.rate_limit_headers()
    try:
        responses_payload = payload.to_responses_request()
        _resolve_auto_model_payload(responses_payload, api_key)
        validate_model_access(api_key, responses_payload.model)
""",
    "chat completions auto routing",
)

api_content = replace_once(
    api_content,
    """    apply_api_key_enforcement(payload, api_key)
    validate_model_access(api_key, payload.model)
    owns_reservation = api_key_reservation_override is None
""",
    """    apply_api_key_enforcement(payload, api_key)
    _resolve_auto_model_payload(payload, api_key)
    validate_model_access(api_key, payload.model)
    owns_reservation = api_key_reservation_override is None
""",
    "stream responses auto routing",
)

api_content = replace_once(
    api_content,
    """    apply_api_key_enforcement(payload, api_key)
    validate_model_access(api_key, payload.model)
    reservation = await _enforce_request_limits(
        api_key,
        request_model=payload.model,
""",
    """    apply_api_key_enforcement(payload, api_key)
    _resolve_auto_model_payload(payload, api_key)
    validate_model_access(api_key, payload.model)
    reservation = await _enforce_request_limits(
        api_key,
        request_model=payload.model,
""",
    "collect responses auto routing",
)

api_content = replace_once(
    api_content,
    """    apply_api_key_enforcement(payload, api_key)
    validate_model_access(api_key, payload.model)
    reservation = await _enforce_request_limits(
        api_key,
        request_model=payload.model,
        request_service_tier=_compact_request_service_tier(payload),
""",
    """    apply_api_key_enforcement(payload, api_key)
    _resolve_auto_model_payload(payload, api_key)
    validate_model_access(api_key, payload.model)
    reservation = await _enforce_request_limits(
        api_key,
        request_model=payload.model,
        request_service_tier=_compact_request_service_tier(payload),
""",
    "compact responses auto routing",
)

api_content = replace_once(
    api_content,
    """def _effective_model_for_api_key(api_key: ApiKeyData | None, requested_model: str) -> str:
""",
    """def _resolve_auto_model_payload(
    payload: ResponsesRequest | ResponsesCompactRequest,
    api_key: ApiKeyData | None,
) -> None:
    if payload.model != _AUTO_MODEL_SLUG:
        return

    model, effort = _select_auto_model_and_reasoning(payload, api_key)
    requested_effort = payload.reasoning.effort if payload.reasoning else None
    payload.model = model.slug
    if payload.reasoning is None:
        payload.reasoning = ResponsesReasoning(effort=effort)
    else:
        payload.reasoning.effort = effort

    logger.info(
        "auto_model_resolved request_id=%s selected_model=%s selected_effort=%s requested_effort=%s",
        get_request_id(),
        payload.model,
        effort,
        requested_effort,
    )


def _select_auto_model_and_reasoning(
    payload: ResponsesRequest | ResponsesCompactRequest,
    api_key: ApiKeyData | None,
) -> tuple[UpstreamModel, str]:
    models = list(get_model_registry().get_models_with_fallback().values())
    allowed_models = _allowed_models_for_api_key(api_key)
    eligible_models = [model for model in models if is_public_model(model, allowed_models)]
    if not eligible_models:
        raise ProxyModelNotAllowed("No available models for auto routing")

    text = _auto_routing_text(payload)
    tier, score = _auto_complexity_tier(payload, text)

    if tier == "SIMPLE":
        preferred_effort = "low"
        preferred_models = ("gpt-5.4-mini", "gpt-5.3-codex", "gpt-5.4", "gpt-5.5")
    elif tier == "MEDIUM":
        preferred_effort = "medium"
        preferred_models = ("gpt-5.4", "gpt-5.3-codex", "gpt-5.4-mini", "gpt-5.5")
    elif tier == "COMPLEX":
        preferred_effort = "medium"
        preferred_models = ("gpt-5.4", "gpt-5.5", "gpt-5.3-codex", "gpt-5.4-mini")
    else:
        preferred_effort = "high"
        preferred_models = ("gpt-5.5", "gpt-5.4", "gpt-5.3-codex", "gpt-5.4-mini")

    selected_model = _pick_auto_model(eligible_models, preferred_models)
    selected_effort = _pick_auto_reasoning_effort(selected_model, preferred_effort)
    logger.info(
        "auto_model_complexity_tier request_id=%s tier=%s score=%.3f selected_model=%s selected_effort=%s",
        get_request_id(),
        tier,
        score,
        selected_model.slug,
        selected_effort,
    )
    return selected_model, selected_effort


def _pick_auto_model(models: list[UpstreamModel], preferred_slugs: tuple[str, ...]) -> UpstreamModel:
    by_slug = {model.slug: model for model in models}
    for slug in preferred_slugs:
        model = by_slug.get(slug)
        if model is not None:
            return model
    return sorted(models, key=lambda model: (-model.priority, model.slug))[0]


def _pick_auto_reasoning_effort(model: UpstreamModel, preferred_effort: str) -> str:
    supported = [level.effort for level in model.supported_reasoning_levels]
    if preferred_effort in supported:
        return preferred_effort
    if model.default_reasoning_level in supported:
        return model.default_reasoning_level
    for fallback in ("medium", "low", "high", "minimal", "xhigh"):
        if fallback in supported:
            return fallback
    return preferred_effort


_AUTO_CODE_KEYWORDS = {
    "function", "class", "def", "async", "await", "api", "endpoint", "database", "sql",
    "docker", "kubernetes", "refactor", "debug", "trace", "stack", "migration", "schema",
    "bug", "fix", "deploy", "production", "integration", "typescript", "python", "javascript",
}

_AUTO_REASONING_PHRASES = (
    "step by step", "think through", "reason through", "analyze carefully", "show your work",
    "root cause", "trade off", "tradeoff", "pros and cons",
)

_AUTO_TECHNICAL_TERMS = {
    "architecture", "distributed", "microservice", "microservices", "orchestration", "security",
    "authentication", "encryption", "performance", "scalability", "consistency", "incident",
    "outage", "compliance", "observability", "pipeline", "queue", "worker", "terraform",
}

_AUTO_SIMPLE_PHRASES = (
    "what is", "define", "translate", "summarize", "quick", "simple", "one liner", "one-liner",
)

_AUTO_MULTI_STEP_PHRASES = (
    "first ", "then ", "after that", "step 1", "step 2", "step 3",
)

_AUTO_OPERATIONAL_PHRASES = (
    "connect and check", "connect to", "check if it works", "see how it works",
    "use devtools", "open the page", "inspect the ui", "debug this", "find the issue",
    "συνδεσου", "συνδέσου", "να συνδεθεις", "να συνδεθείς",
    "δες πως δουλευει", "δες πως δουλεύει", "αν δουλευει", "αν δουλεύει",
    "ελεγξε", "έλεγξε", "να ελεγξεις", "να ελέγξεις",
    "ψαξε", "ψάξε", "βρες το προβλημα", "βρες το πρόβλημα",
    "χρησιμοποιησε devtools", "χρησιμοποίησε devtools", "ανοιξε τη σελιδα", "άνοιξε τη σελίδα",
)


def _auto_complexity_tier(payload: ResponsesRequest | ResponsesCompactRequest, text: str) -> tuple[str, float]:
    lowered = text.lower().strip()
    words = _auto_normalized_words(lowered)
    word_set = set(words)
    token_count = len(words)

    if not lowered:
        return "SIMPLE", 0.0

    reasoning_hits = _auto_phrase_hits(lowered, _AUTO_REASONING_PHRASES)
    if reasoning_hits >= 2:
        return "REASONING", 1.0

    score = 0.0

    if token_count <= 15:
        score -= 0.08
    elif token_count >= 400:
        score += 0.10
    elif token_count >= 120:
        score += 0.05

    code_hits = _auto_keyword_hits(word_set, _AUTO_CODE_KEYWORDS)
    if code_hits:
        score += min(0.30, 0.08 * code_hits)

    if reasoning_hits:
        score += min(0.25, 0.12 * reasoning_hits)

    technical_hits = _auto_keyword_hits(word_set, _AUTO_TECHNICAL_TERMS)
    if technical_hits:
        score += min(0.25, 0.07 * technical_hits)

    if _auto_phrase_hits(lowered, _AUTO_SIMPLE_PHRASES):
        score -= 0.05

    if _auto_phrase_hits(lowered, _AUTO_MULTI_STEP_PHRASES):
        score += 0.03

    operational_hits = _auto_phrase_hits(lowered, _AUTO_OPERATIONAL_PHRASES)
    if operational_hits:
        score += min(0.35, 0.22 * operational_hits)

    question_marks = lowered.count("?")
    if question_marks >= 2:
        score += min(0.02, 0.01 * (question_marks - 1))

    if getattr(payload, "tools", None):
        score += 0.08

    if any(keyword in lowered for keyword in ("critical", "urgent", "data loss", "security breach", "production down")):
        score += 0.20

    score = max(0.0, min(score, 1.0))
    if score < 0.15:
        return "SIMPLE", score
    if score < 0.35:
        return "MEDIUM", score
    if score < 0.60:
        return "COMPLEX", score
    return "REASONING", score



def _auto_normalized_words(text: str) -> list[str]:
    chars: list[str] = []
    words: list[str] = []
    for ch in text:
        if ch.isalnum():
            chars.append(ch)
            continue
        if chars:
            words.append("".join(chars))
            chars = []
    if chars:
        words.append("".join(chars))
    return words



def _auto_keyword_hits(words: set[str], keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in words)



def _auto_phrase_hits(text: str, phrases: tuple[str, ...]) -> int:
    return sum(1 for phrase in phrases if phrase in text)


def _auto_routing_text(payload: ResponsesRequest | ResponsesCompactRequest) -> str:
    latest = _latest_user_text(getattr(payload, "input", None))
    if latest.strip():
        return latest
    return _auto_payload_text(payload)


def _latest_user_text(value: JsonValue) -> str:
    if isinstance(value, list):
        for item in reversed(value):
            if isinstance(item, Mapping) and item.get("role") == "user":
                parts: list[str] = []
                _collect_auto_text(item.get("content"), parts)
                text = "\\n".join(parts).strip()
                if text:
                    return text
            nested = _latest_user_text(item)
            if nested.strip():
                return nested
    if isinstance(value, Mapping):
        role = value.get("role")
        if role == "user":
            parts: list[str] = []
            _collect_auto_text(value.get("content"), parts)
            text = "\\n".join(parts).strip()
            if text:
                return text
        for key in ("input", "messages", "content"):
            nested = value.get(key)
            if nested is not None:
                text = _latest_user_text(nested)
                if text.strip():
                    return text
    return ""


def _auto_payload_text(payload: ResponsesRequest | ResponsesCompactRequest) -> str:
    parts: list[str] = []
    instructions = getattr(payload, "instructions", None)
    if isinstance(instructions, str):
        parts.append(instructions)
    _collect_auto_text(getattr(payload, "input", None), parts)
    return "\\n".join(parts)


def _collect_auto_text(value: JsonValue, parts: list[str]) -> None:
    if isinstance(value, str):
        parts.append(value)
        return
    if isinstance(value, list):
        for item in value:
            _collect_auto_text(item, parts)
        return
    if isinstance(value, Mapping):
        for key in ("text", "input_text", "output_text", "content"):
            nested = value.get(key)
            if nested is not None:
                _collect_auto_text(nested, parts)



def _effective_model_for_api_key(api_key: ApiKeyData | None, requested_model: str) -> str:
""",
    "auto routing helpers",
)

API_FILE.write_text(api_content)
print("patched", API_FILE)
