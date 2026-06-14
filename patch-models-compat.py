from pathlib import Path


API_FILE = Path("/app/app/modules/proxy/api.py")
MAIN_FILE = Path("/app/app/main.py")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"target snippet not found: {label}")
    return content.replace(old, new, 1)


api_content = API_FILE.read_text()

api_content = replace_once(
    api_content,
    """v1_router = APIRouter(
    prefix="/v1",
    tags=["proxy"],
    dependencies=[Security(validate_proxy_api_key), Depends(set_openai_error_format)],
)
v1_ws_router = APIRouter(
    prefix="/v1",
    tags=["proxy"],
)
""",
    """v1_router = APIRouter(
    prefix="/v1",
    tags=["proxy"],
    dependencies=[Security(validate_proxy_api_key), Depends(set_openai_error_format)],
)
compat_router = APIRouter(
    tags=["proxy"],
)
v1_ws_router = APIRouter(
    prefix="/v1",
    tags=["proxy"],
)
""",
    "compat router declaration",
)

api_content = replace_once(
    api_content,
    """@v1_router.get("/models", response_model=ModelListResponse)
async def v1_models(
    api_key: ApiKeyData | None = Security(validate_proxy_api_key),
) -> Response:
    return await _build_models_response(api_key)


@v1_router.get("/usage", response_model=V1UsageResponse)
""",
    """@v1_router.get("/models", response_model=ModelListResponse)
async def v1_models(
    api_key: ApiKeyData | None = Security(validate_proxy_api_key),
) -> JSONResponse:
    return JSONResponse(content=_build_models_payload(api_key))


@compat_router.get("/api/v1/models")
async def compat_api_v1_models() -> JSONResponse:
    return JSONResponse(content=_build_public_models_payload())


@compat_router.get("/api/tags")
async def compat_api_tags() -> JSONResponse:
    return JSONResponse(content=_build_ollama_tags_payload())


@compat_router.get("/v1/props")
@compat_router.get("/props")
async def compat_props() -> JSONResponse:
    return JSONResponse(content=_build_compat_props_payload())


@compat_router.get("/version")
async def compat_version() -> JSONResponse:
    return JSONResponse(
        content={
            "service": "codex-lb",
            "version": "0.1.0",
            "client_version": get_settings().model_registry_client_version,
        }
    )


@v1_router.get("/usage", response_model=V1UsageResponse)
""",
    "compat route aliases",
)

api_content = replace_once(
    api_content,
    """def _allowed_models_for_api_key(api_key: ApiKeyData | None) -> set[str] | None:
    allowed_models = set(api_key.allowed_models) if api_key and api_key.allowed_models else None
    if api_key and api_key.enforced_model:
        forced = {api_key.enforced_model}
        return forced if allowed_models is None else (allowed_models & forced)
    return allowed_models
""",
    """def _build_model_entries(api_key: ApiKeyData | None) -> tuple[list[ModelListItem], list[CodexModelEntry]]:
    created = int(time.time())
    registry = get_model_registry()
    models = registry.get_models_with_fallback()
    allowed_models = _allowed_models_for_api_key(api_key)

    items: list[ModelListItem] = []
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


def _build_models_payload(api_key: ApiKeyData | None) -> dict[str, JsonValue]:
    items, codex_entries = _build_model_entries(api_key)
    payload = ModelListResponse(data=items).model_dump(mode="json")
    payload["models"] = CodexModelsResponse(models=codex_entries).model_dump(mode="json")["models"]
    return cast(dict[str, JsonValue], payload)


def _build_public_models_payload() -> dict[str, JsonValue]:
    return _build_models_payload(None)


def _build_compat_props_payload() -> dict[str, JsonValue]:
    return {
        "provider": "codex-lb",
        "service": "codex-lb",
        "service_version": "0.1.0",
        "client_version": get_settings().model_registry_client_version,
        "compatibility": {
            "openai_responses": True,
            "openai_chat_completions": True,
            "model_listing": True,
            "transcriptions": True,
            "ollama_tags_probe": True,
        },
        "endpoints": {
            "responses": "/v1/responses",
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models",
            "compat_models": "/api/v1/models",
            "compat_tags": "/api/tags",
        },
    }


def _build_ollama_tags_payload() -> dict[str, JsonValue]:
    _, codex_entries = _build_model_entries(None)
    modified_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "models": [
            {
                "name": entry.slug,
                "model": entry.slug,
                "modified_at": modified_at,
                "size": 0,
                "digest": entry.slug,
                "details": {
                    "family": "codex",
                    "families": ["codex", "openai"],
                    "format": "openai",
                    "parameter_size": "unknown",
                    "quantization_level": "unknown",
                },
            }
            for entry in codex_entries
        ]
    }


def _allowed_models_for_api_key(api_key: ApiKeyData | None) -> set[str] | None:
    allowed_models = set(api_key.allowed_models) if api_key and api_key.allowed_models else None
    if api_key and api_key.enforced_model:
        forced = {api_key.enforced_model}
        return forced if allowed_models is None else (allowed_models & forced)
    return allowed_models
""",
    "compat helper functions",
)

API_FILE.write_text(api_content)
print("patched", API_FILE)

main_content = MAIN_FILE.read_text()
main_content = replace_once(
    main_content,
    """    app.include_router(proxy_api.v1_router)
    app.include_router(proxy_api.v1_ws_router)
""",
    """    app.include_router(proxy_api.v1_router)
    app.include_router(proxy_api.compat_router)
    app.include_router(proxy_api.v1_ws_router)
""",
    "compat router inclusion",
)
MAIN_FILE.write_text(main_content)
print("patched", MAIN_FILE)
