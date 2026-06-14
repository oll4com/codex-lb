from pathlib import Path


OAUTH_SCHEMAS_FILE = Path("/app/app/modules/oauth/schemas.py")
OAUTH_SERVICE_FILE = Path("/app/app/modules/oauth/service.py")
OAUTH_API_FILE = Path("/app/app/modules/oauth/api.py")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"target snippet not found: {label}")
    return content.replace(old, new, 1)


schemas_content = OAUTH_SCHEMAS_FILE.read_text()
schemas_content = replace_once(
    schemas_content,
    """class OauthStartRequest(DashboardModel):
    force_method: str | None = None
""",
    """class OauthStartRequest(DashboardModel):
    force_method: str | None = None
    provider: str = "openai"
""",
    "oauth start request provider field",
)
OAUTH_SCHEMAS_FILE.write_text(schemas_content)
print("patched", OAUTH_SCHEMAS_FILE)


service_content = OAUTH_SERVICE_FILE.read_text()
service_content = replace_once(
    service_content,
    """    async def start_oauth(self, request: OauthStartRequest) -> OauthStartResponse:
        force_method = (request.force_method or "").lower()
        if not force_method:
""",
    """    async def start_oauth(self, request: OauthStartRequest) -> OauthStartResponse:
        provider = (request.provider or "openai").strip().lower()
        if provider not in {"openai", "chatgpt"}:
            raise OAuthError(
                "provider_not_supported",
                f"OAuth provider '{provider}' is not enabled in this build.",
                501,
            )

        force_method = (request.force_method or "").lower()
        if not force_method:
""",
    "oauth service provider guard",
)
OAUTH_SERVICE_FILE.write_text(service_content)
print("patched", OAUTH_SERVICE_FILE)


api_content = OAUTH_API_FILE.read_text()
api_content = replace_once(
    api_content,
    """    except OAuthError as exc:
        return JSONResponse(
            status_code=502,
            content=dashboard_error(exc.code, exc.message),
        )
""",
    """    except OAuthError as exc:
        return JSONResponse(
            status_code=exc.status_code or 502,
            content=dashboard_error(exc.code, exc.message),
        )
""",
    "oauth api status passthrough",
)
OAUTH_API_FILE.write_text(api_content)
print("patched", OAUTH_API_FILE)
