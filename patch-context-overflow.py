from pathlib import Path


SERVICE_FILE = Path("/app/app/modules/proxy/service.py")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"target snippet not found: {label}")
    return content.replace(old, new, 1)


content = SERVICE_FILE.read_text()

content = replace_once(
    content,
    "_UPSTREAM_RESPONSE_CREATE_WARN_BYTES = 12 * 1024 * 1024\n"
    "_UPSTREAM_RESPONSE_CREATE_MAX_BYTES = 15 * 1024 * 1024\n",
    "_UPSTREAM_RESPONSE_CREATE_WARN_BYTES = 12 * 1024 * 1024\n"
    "_UPSTREAM_RESPONSE_CREATE_MAX_BYTES = 15 * 1024 * 1024\n"
    "_UPSTREAM_RESPONSE_CREATE_AUTO_TRUNCATE_BYTES = 512 * 1024\n"
    "_UPSTREAM_RESPONSE_CREATE_CONTEXT_RECOVERY_TARGET_BYTES = 900 * 1024\n",
    "response.create size constants",
)

content = replace_once(
    content,
    """        text_data = json.dumps(upstream_payload, ensure_ascii=True, separators=(",", ":"))
        payload_size = len(text_data.encode("utf-8"))
        if payload_size > _UPSTREAM_RESPONSE_CREATE_MAX_BYTES:
""",
    """        text_data = json.dumps(upstream_payload, ensure_ascii=True, separators=(",", ":"))
        payload_size = len(text_data.encode("utf-8"))
        if _should_force_response_create_auto_truncation(upstream_payload, payload_size):
            upstream_payload["truncation"] = "auto"
            text_data = json.dumps(upstream_payload, ensure_ascii=True, separators=(",", ":"))
            logger.warning(
                "Forced response.create truncation=auto request_id=%s request_log_id=%s "
                "transport=%s bytes=%s model=%s",
                request_state.request_id,
                request_state.request_log_id,
                transport,
                len(text_data.encode("utf-8")),
                request_state.model,
            )
            payload_size = len(text_data.encode("utf-8"))
        if payload_size > _UPSTREAM_RESPONSE_CREATE_MAX_BYTES:
""",
    "force auto truncation before size slimming",
)

content = replace_once(
    content,
    """            should_attempt_context_overflow_fresh_turn_recovery = (
                is_context_overflow
                and effective_payload.previous_response_id is not None
                and bridge_session_key.strength != "hard"
            )
""",
    """            context_overflow_retry_payload = (
                _http_bridge_context_overflow_retry_payload(effective_payload) if is_context_overflow else None
            )
            should_attempt_context_overflow_fresh_turn_recovery = context_overflow_retry_payload is not None
""",
    "context overflow retry decision",
)

content = replace_once(
    content,
    """                recovery_path = "context_overflow_fresh_turn"
                retry_payload = _http_bridge_payload_without_previous_response_id(effective_payload)
                retry_previous_response_id = None
""",
    """                recovery_path = "context_overflow_fresh_turn"
                assert context_overflow_retry_payload is not None
                retry_payload = context_overflow_retry_payload
                retry_previous_response_id = None
""",
    "context overflow retry payload",
)

content = replace_once(
    content,
    """def _response_create_history_omission_notice_item(count: int) -> dict[str, JsonValue]:
    return {
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": _RESPONSE_CREATE_HISTORY_OMISSION_NOTICE.format(count=count),
            }
        ],
    }


def _is_inline_image_reference(value: JsonValue) -> bool:
""",
    """def _response_create_history_omission_notice_item(count: int) -> dict[str, JsonValue]:
    return {
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": _RESPONSE_CREATE_HISTORY_OMISSION_NOTICE.format(count=count),
            }
        ],
    }


def _should_force_response_create_auto_truncation(payload: Mapping[str, JsonValue], payload_size: int) -> bool:
    # The current upstream bridge rejects `truncation`, so never inject it here.
    return False


def _http_bridge_context_overflow_retry_payload(payload: ResponsesRequest) -> ResponsesRequest | None:
    retry_input = _response_create_context_recovery_input(payload.input)
    if retry_input is None and payload.previous_response_id is None:
        return None
    updates: dict[str, JsonValue] = {"previous_response_id": None}
    if retry_input is not None:
        updates["input"] = retry_input
    return payload.model_copy(update=updates)


def _response_create_context_recovery_input(input_value: JsonValue) -> JsonValue | None:
    if not isinstance(input_value, list) or len(input_value) <= 1:
        return None

    input_items = cast(list[JsonValue], input_value)
    recent_start = max(_response_create_recent_suffix_start(input_items), len(input_items) - 24)
    recent_items = input_items[recent_start:]
    omitted_count = recent_start
    slimmed_recent: list[JsonValue] = []
    tool_outputs_slimmed = 0
    images_slimmed = 0
    for item in recent_items:
        slimmed_item, item_tool_outputs_slimmed, item_images_slimmed = _slim_historical_response_input_item(item)
        slimmed_recent.append(slimmed_item)
        tool_outputs_slimmed += item_tool_outputs_slimmed
        images_slimmed += item_images_slimmed

    candidate_items: list[JsonValue] = []
    if omitted_count > 0:
        candidate_items.append(_response_create_history_omission_notice_item(omitted_count))
    candidate_items.extend(slimmed_recent)

    while (
        len(candidate_items) > 2
        and _response_create_input_size(candidate_items) > _UPSTREAM_RESPONSE_CREATE_CONTEXT_RECOVERY_TARGET_BYTES
    ):
        if is_json_mapping(candidate_items[0]) and candidate_items[0].get("role") == "assistant":
            if len(candidate_items) <= 3:
                break
            candidate_items.pop(1)
        else:
            candidate_items.pop(0)
        omitted_count += 1
        if candidate_items and is_json_mapping(candidate_items[0]) and candidate_items[0].get("role") == "assistant":
            candidate_items[0] = _response_create_history_omission_notice_item(omitted_count)

    logger.warning(
        "Prepared context-overflow recovery input original_items=%s retry_items=%s omitted_items=%s "
        "tool_outputs_slimmed=%s images_slimmed=%s retry_input_bytes=%s",
        len(input_items),
        len(candidate_items),
        omitted_count,
        tool_outputs_slimmed,
        images_slimmed,
        _response_create_input_size(candidate_items),
    )
    return candidate_items


def _response_create_input_size(input_items: list[JsonValue]) -> int:
    return len(json.dumps(input_items, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))


def _is_inline_image_reference(value: JsonValue) -> bool:
""",
    "context overflow recovery helpers",
)

SERVICE_FILE.write_text(content)
print(f"patched {SERVICE_FILE}")
