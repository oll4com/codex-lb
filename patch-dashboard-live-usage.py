from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path('/app/app/static/assets')


def patch_asset(path: Path) -> bool:
    text = path.read_text()
    original = text
    old_schema = 'uv=oe({accountId:B(),email:B(),displayName:B(),planType:B(),status:B(),usage:Xk.nullable().optional(),resetAtPrimary:B().datetime({offset:!0}).nullable().optional(),resetAtSecondary:B().datetime({offset:!0}).nullable().optional(),windowMinutesPrimary:fe().nullable().optional(),windowMinutesSecondary:fe().nullable().optional(),requestUsage:Jk.nullable().optional(),auth:Pk.nullable().optional(),additionalQuotas:$e(cv).default([])})'
    new_schema = 'uv=oe({accountId:B(),email:B(),displayName:B(),planType:B(),status:B(),usage:Xk.nullable().optional(),resetAtPrimary:B().datetime({offset:!0}).nullable().optional(),resetAtSecondary:B().datetime({offset:!0}).nullable().optional(),windowMinutesPrimary:fe().nullable().optional(),windowMinutesSecondary:fe().nullable().optional(),requestUsage:Jk.nullable().optional(),auth:Pk.nullable().optional(),additionalQuotas:$e(cv).default([]),activeRequestCount:fe().int().nonnegative().default(0),recentlySelected:st().default(!1),lastSelectedAt:B().datetime({offset:!0}).nullable().optional(),lastLiveStartedAt:B().datetime({offset:!0}).nullable().optional(),liveRequestId:B().nullable().optional(),liveModel:B().nullable().optional(),liveTransport:B().nullable().optional()})'
    if old_schema in text:
        text = text.replace(old_schema, new_schema, 1)
    elif new_schema not in text:
        raise RuntimeError(f'{path}: account summary schema target not found')

    old_fn_prefix = 'function wE({account:t,showAccountId:a=!1,onAction:l}){const o=Ns($=>$.blurred),u=Jv(t.status),f=t.usage?.primaryRemainingPercent??null,m=t.usage?.secondaryRemainingPercent??null,p=t.windowMinutesPrimary==null&&t.windowMinutesSecondary!=null,y=Sf(t.resetAtPrimary??null),g=Sf(t.resetAtSecondary??null),b=t.displayName||t.email,x=Ec(t.accountId),w=mr(t.planType),j=t.displayName&&t.displayName!==t.email?t.email:null,O=a?` | ID ${x}`:"";return i.jsxs("div",{className:"card-hover rounded-xl border bg-card p-4",children:'
    new_fn_prefix = 'function wE({account:t,showAccountId:a=!1,onAction:l}){const o=Ns($=>$.blurred),u=Jv(t.status),f=t.usage?.primaryRemainingPercent??null,m=t.usage?.secondaryRemainingPercent??null,p=t.windowMinutesPrimary==null&&t.windowMinutesSecondary!=null,y=Sf(t.resetAtPrimary??null),g=Sf(t.resetAtSecondary??null),b=t.displayName||t.email,x=Ec(t.accountId),w=mr(t.planType),j=t.displayName&&t.displayName!==t.email?t.email:null,O=a?` | ID ${x}`:"",$=(t.activeRequestCount??0)>0,L=$||!!t.recentlySelected,D=t.liveModel?`${$?"Using now":"Recently used"} · ${t.liveModel}`:$?"Using now":"Recently used";return i.jsxs("div",{className:"card-hover rounded-xl border bg-card p-4",children:'
    if old_fn_prefix in text:
        text = text.replace(old_fn_prefix, new_fn_prefix, 1)
    elif new_fn_prefix not in text:
        raise RuntimeError(f'{path}: account card prefix target not found')

    old_email = 'i.jsx("p",{className:"truncate text-sm font-semibold leading-tight",children:o?i.jsx("span",{className:"privacy-blur",children:b}):b})'
    new_email = 'i.jsxs("p",{className:"flex min-w-0 items-center gap-1.5 text-sm font-semibold leading-tight",children:[i.jsx("span",{className:ce("truncate",o?"privacy-blur":void 0),children:b}),L?i.jsxs("span",{className:"inline-flex shrink-0 items-center rounded-full border border-rose-500/35 bg-rose-500/10 px-1.5 py-[1px] text-[8px] font-semibold uppercase tracking-normal text-rose-300",title:D,children:[i.jsx("span",{className:ce("h-1 w-1 rounded-full",$?"animate-pulse bg-rose-400":"bg-rose-300")}),(t.activeRequestCount??0)>1?`Live x${t.activeRequestCount}`:$?"Live":"Recent"]}):null]})'
    if old_email in text:
        text = text.replace(old_email, new_email, 1)
    elif new_email not in text:
        raise RuntimeError(f'{path}: account email live target not found')

    old_status = 'i.jsx(Wv,{status:u})]}),i.jsxs("div",{className:ce("mt-3.5 grid gap-3",p?"grid-cols-1":"grid-cols-2"),children:'
    new_status = 'i.jsx(Wv,{status:u})]}),i.jsxs("div",{className:ce("mt-3.5 grid gap-3",p?"grid-cols-1":"grid-cols-2"),children:'
    if old_status in text:
        text = text.replace(old_status, new_status, 1)
    elif new_status not in text:
        raise RuntimeError(f'{path}: account live status target not found')

    old_refetch = 'function FE(t=fr){return On({queryKey:["dashboard","overview",t],queryFn:()=>mv({timeframe:t}),refetchInterval:3e4,refetchIntervalInBackground:!1,refetchOnWindowFocus:!0})}'
    new_refetch = 'function FE(t=fr){return On({queryKey:["dashboard","overview",t],queryFn:()=>mv({timeframe:t}),refetchInterval:5e3,refetchIntervalInBackground:!0,refetchOnWindowFocus:!0})}'
    if old_refetch in text:
        text = text.replace(old_refetch, new_refetch, 1)
    elif new_refetch not in text:
        raise RuntimeError(f'{path}: dashboard refetch target not found')

    text = text.replace(
        'className:"grid auto-rows-[236px] gap-4 sm:grid-cols-2 lg:grid-cols-3",children:o.map',
        'className:"grid gap-4 sm:grid-cols-2 lg:grid-cols-3",children:o.map',
    )
    text = text.replace(
        'className:"animate-fade-in-up h-full",style:{animationDelay:`${f*75}ms`},children:i.jsx(wE',
        'className:"animate-fade-in-up",style:{animationDelay:`${f*75}ms`},children:i.jsx(wE',
    )
    text = text.replace(
        'i.jsxs("div",{className:"mt-auto flex items-center gap-1.5 border-t pt-3",children:',
        'i.jsxs("div",{className:"mt-3 flex items-center gap-1.5 border-t pt-3",children:',
    )
    text = text.replace(
        'i.jsxs("div",{className:"mt-3 flex items-center gap-1.5 border-t pt-3",children:[',
        'i.jsxs("div",{className:"mt-3 flex items-center gap-1.5 border-t pt-3",children:[',
    )
    details_tail = 'u==="deactivated"&&i.jsxs(je,{type:"button",size:"sm",variant:"ghost",className:"h-7 gap-1.5 rounded-lg text-xs text-amber-600 hover:bg-amber-500/10 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-300",onClick:()=>l?.(t,"reauth"),children:[i.jsx(hy,{className:"h-3 w-3"}),"Re-auth"]})]})]})}const'
    details_tail_new = 'u==="deactivated"&&i.jsxs(je,{type:"button",size:"sm",variant:"ghost",className:"h-7 gap-1.5 rounded-lg text-xs text-amber-600 hover:bg-amber-500/10 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-300",onClick:()=>l?.(t,"reauth"),children:[i.jsx(hy,{className:"h-3 w-3"}),"Re-auth"]}),L?i.jsxs("span",{className:"ml-auto max-w-[52%] truncate text-right text-xs font-medium text-muted-foreground/70",title:D,children:[i.jsx("span",{className:"text-muted-foreground/50",children:$?"Using now":"Recently used"}),t.liveModel?i.jsxs("span",{className:"ml-1 text-muted-foreground/80",children:["· ",t.liveModel]}):null]}):null]})]})}const'
    if details_tail in text:
        text = text.replace(details_tail, details_tail_new, 1)
    elif details_tail_new not in text:
        raise RuntimeError(f'{path}: account details using-now target not found')

    if text != original:
        path.write_text(text)
        return True
    return False


def main() -> None:
    patched = []
    for asset in ASSETS_DIR.glob('*.js'):
        try:
            if patch_asset(asset):
                patched.append(asset.name)
        except RuntimeError as exc:
            if asset.name.startswith('index-'):
                raise
    print('patched dashboard live usage assets:', ', '.join(patched))


if __name__ == '__main__':
    main()
