from pathlib import Path


SCHEMAS_FILE = Path("/app/app/modules/oauth/schemas.py")
SERVICE_FILE = Path("/app/app/modules/oauth/service.py")
INDEX_FILE = Path("/app/app/static/assets/index-CNlFECW2.js")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"target snippet not found: {label}")
    return content.replace(old, new, 1)


schemas = SCHEMAS_FILE.read_text()
schemas = replace_once(
    schemas,
    """class OauthStartRequest(DashboardModel):
    force_method: str | None = None
    provider: str = "openai"
""",
    """class OauthStartRequest(DashboardModel):
    force_method: str | None = None
    provider: str = "openai"
    account_id: str | None = None
""",
    "OAuth start account_id schema",
)
SCHEMAS_FILE.write_text(schemas)
print("patched", SCHEMAS_FILE)


service = SERVICE_FILE.read_text()
service = replace_once(
    service,
    """    poll_task: asyncio.Task[None] | None = None
""",
    """    poll_task: asyncio.Task[None] | None = None
    target_account_id: str | None = None
""",
    "OAuth state target account id",
)
service = replace_once(
    service,
    """        force_method = (request.force_method or "").lower()
        if not force_method:
""",
    """        target_account_id = (request.account_id or "").strip() or None
        if target_account_id and not await self._accounts_repo.get_by_id(target_account_id):
            raise OAuthError(
                "account_not_found",
                f"Account '{target_account_id}' was not found for re-authentication.",
                404,
            )

        force_method = (request.force_method or "").lower()
        if not force_method and not target_account_id:
""",
    "OAuth start target validation",
)
service = replace_once(
    service,
    """        if force_method == "device":
            return await self._start_device_flow()

        try:
            return await self._start_browser_flow()
        except OSError:
            return await self._start_device_flow()
""",
    """        if force_method == "device":
            return await self._start_device_flow(target_account_id=target_account_id)

        try:
            return await self._start_browser_flow(target_account_id=target_account_id)
        except OSError:
            return await self._start_device_flow(target_account_id=target_account_id)
""",
    "OAuth start target propagation",
)
service = replace_once(
    service,
    """    async def _start_browser_flow(self) -> OauthStartResponse:
        await self._store.reset()
""",
    """    async def _start_browser_flow(self, *, target_account_id: str | None = None) -> OauthStartResponse:
        await self._store.reset()
""",
    "OAuth browser target signature",
)
service = replace_once(
    service,
    """            state.error_message = None

        callback_server = OAuthCallbackServer(
""",
    """            state.error_message = None
            state.target_account_id = target_account_id

        callback_server = OAuthCallbackServer(
""",
    "OAuth browser state target",
)
service = replace_once(
    service,
    """    async def _start_device_flow(self) -> OauthStartResponse:
        await self._store.reset()
""",
    """    async def _start_device_flow(self, *, target_account_id: str | None = None) -> OauthStartResponse:
        await self._store.reset()
""",
    "OAuth device target signature",
)
service = replace_once(
    service,
    """            state.error_message = None

        return OauthStartResponse(
""",
    """            state.error_message = None
            state.target_account_id = target_account_id

        return OauthStartResponse(
""",
    "OAuth device state target",
)
service = replace_once(
    service,
    """        account = Account(
            id=account_id,
            chatgpt_account_id=raw_account_id,
            email=email,
            plan_type=plan_type,
            access_token_encrypted=self._encryptor.encrypt(tokens.access_token),
            refresh_token_encrypted=self._encryptor.encrypt(tokens.refresh_token),
            id_token_encrypted=self._encryptor.encrypt(tokens.id_token),
            last_refresh=utcnow(),
            status=AccountStatus.ACTIVE,
            deactivation_reason=None,
        )
        if self._repo_factory:
            async with self._repo_factory() as repo:
                await repo.upsert(account)
        else:
            await self._accounts_repo.upsert(account)
""",
    """        access_token_encrypted = self._encryptor.encrypt(tokens.access_token)
        refresh_token_encrypted = self._encryptor.encrypt(tokens.refresh_token)
        id_token_encrypted = self._encryptor.encrypt(tokens.id_token)
        last_refresh = utcnow()

        account = Account(
            id=account_id,
            chatgpt_account_id=raw_account_id,
            email=email,
            plan_type=plan_type,
            access_token_encrypted=access_token_encrypted,
            refresh_token_encrypted=refresh_token_encrypted,
            id_token_encrypted=id_token_encrypted,
            last_refresh=last_refresh,
            status=AccountStatus.ACTIVE,
            deactivation_reason=None,
        )

        async with self._store.lock:
            target_account_id = self._store.state.target_account_id

        async def persist_with_repo(repo: AccountsRepository) -> None:
            if not target_account_id:
                await repo.upsert(account)
                return

            existing = await repo.get_by_id(target_account_id)
            if existing is None:
                raise OAuthError(
                    "account_not_found",
                    f"Account '{target_account_id}' was not found for re-authentication.",
                    404,
                )

            existing_email = (existing.email or "").strip().lower()
            new_email = (email or "").strip().lower()
            if (
                existing_email
                and new_email
                and existing_email != DEFAULT_EMAIL
                and new_email != DEFAULT_EMAIL
                and existing_email != new_email
            ):
                raise OAuthError(
                    "account_email_mismatch",
                    f"Authenticated email '{email}' does not match account '{existing.email}'.",
                    409,
                )

            updated = await repo.update_tokens(
                target_account_id,
                access_token_encrypted,
                refresh_token_encrypted,
                id_token_encrypted,
                last_refresh,
                plan_type=plan_type,
                email=email,
                chatgpt_account_id=raw_account_id,
            )
            if not updated:
                raise OAuthError(
                    "account_not_found",
                    f"Account '{target_account_id}' was not found for re-authentication.",
                    404,
                )
            await repo.update_status(target_account_id, AccountStatus.ACTIVE, None, None, blocked_at=None)

        if self._repo_factory:
            async with self._repo_factory() as repo:
                await persist_with_repo(repo)
        else:
            await persist_with_repo(self._accounts_repo)
""",
    "OAuth persist target update",
)
SERVICE_FILE.write_text(service)
print("patched", SERVICE_FILE)


index_content = INDEX_FILE.read_text()
index_content = replace_once(
    index_content,
    "nA=oe({forceMethod:B().optional(),provider:B().optional()})",
    "nA=oe({forceMethod:B().optional(),provider:B().optional(),accountId:B().optional()})",
    "frontend OAuth start schema accountId",
)
index_content = replace_once(
    index_content,
    """y=E.useCallback(async(x,W)=>{u(),f(),a(w=>({...w,status:"starting",errorMessage:null}));try{const j=await cT({forceMethod:x,provider:W??"openai"}),O=pa.parse({status:"pending",method:j.method==="device"?"device":"browser",authorizationUrl:j.authorizationUrl,callbackUrl:j.callbackUrl,verificationUrl:j.verificationUrl,userCode:j.userCode,deviceAuthId:j.deviceAuthId,intervalSeconds:j.intervalSeconds,expiresInSeconds:j.expiresInSeconds,errorMessage:null});return a(O),O.method==="device"&&O.deviceAuthId&&O.userCode&&await _0({deviceAuthId:O.deviceAuthId,userCode:O.userCode}),O}catch(j){const O=j instanceof Error?j.message:"Failed to start OAuth";throw a(P=>pa.parse({...P,status:"error",errorMessage:O})),j}},""",
    """y=E.useCallback(async(x,W,P)=>{u(),f(),a(w=>({...w,status:"starting",errorMessage:null}));try{const j=await cT({forceMethod:x,provider:W??"openai",accountId:P??void 0}),O=pa.parse({status:"pending",method:j.method==="device"?"device":"browser",authorizationUrl:j.authorizationUrl,callbackUrl:j.callbackUrl,verificationUrl:j.verificationUrl,userCode:j.userCode,deviceAuthId:j.deviceAuthId,intervalSeconds:j.intervalSeconds,expiresInSeconds:j.expiresInSeconds,errorMessage:null});return a(O),O.method==="device"&&O.deviceAuthId&&O.userCode&&await _0({deviceAuthId:O.deviceAuthId,userCode:O.userCode}),O}catch(j){const O=j instanceof Error?j.message:"Failed to start OAuth";throw a(P0=>pa.parse({...P0,status:"error",errorMessage:O})),j}},""",
    "frontend OAuth start accountId payload",
)
index_content = replace_once(
    index_content,
    "onReauth:()=>g.show()})]}):i.jsx(kT,{})",
    "onReauth:()=>g.show(L?.accountId??void 0)})]}):i.jsx(kT,{})",
    "frontend reauth selected account target",
)
index_content = replace_once(
    index_content,
    "onStart:async(W,P)=>{await p.start(W,P)}",
    "onStart:async(W,P)=>{await p.start(W,P,g.data??void 0)}",
    "frontend dialog onStart target argument",
)
INDEX_FILE.write_text(index_content)
print("patched", INDEX_FILE)
