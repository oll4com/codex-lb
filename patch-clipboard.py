from pathlib import Path
import re

ASSETS_DIR = Path('/app/app/static/assets')
INDEX_HTML = Path('/app/app/static/index.html')
copy_logic = 'if(typeof navigator<"u"&&navigator.clipboard?.writeText&&typeof window<"u"&&window.isSecureContext)await navigator.clipboard.writeText(t);else{let c=!1;const u=m=>{m.clipboardData&&(m.clipboardData.setData("text/plain",t),m.preventDefault(),c=!0)};document.addEventListener("copy",u);try{document.execCommand("copy")}finally{document.removeEventListener("copy",u)}if(!c){const m=document.createElement("textarea");m.value=t,m.setAttribute("readonly","readonly"),m.style.position="fixed",m.style.left="-9999px",m.style.top="0",document.body.appendChild(m),m.focus(),m.select(),m.setSelectionRange(0,m.value.length);const p=document.execCommand("copy");document.body.removeChild(m);if(!p)throw new Error("copy-failed")}}'
patterns = [
    (re.compile(r'await navigator\.clipboard\.writeText\(t\),u\(!0\),Oe\.success\("Copied to clipboard"\),setTimeout\(\(\)=>u\(!1\),1200\)'), copy_logic + 'u(!0),Oe.success("Copied to clipboard"),setTimeout(()=>u(!1),1200)'),
    (re.compile(r'await navigator\.clipboard\.writeText\(t\),i\(!0\),setTimeout\(\(\)=>i\(!1\),2e3\)'), copy_logic + 'i(!0),setTimeout(()=>i(!1),2e3)'),
]
patched = []
for asset in ASSETS_DIR.glob('*.js'):
    content = asset.read_text()
    total = 0
    for pattern, replacement in patterns:
        content, count = pattern.subn(replacement, content)
        total += count
    content = content.replace('}},u(!0),Oe.success("Copied to clipboard"),setTimeout(()=>u(!1),1200)}catch', '}u(!0),Oe.success("Copied to clipboard"),setTimeout(()=>u(!1),1200)}catch')
    content = content.replace('}},i(!0),setTimeout(()=>i(!1),2e3)},[t])', '}i(!0),setTimeout(()=>i(!1),2e3)},[t])')
    if total or 'clipboardData.setData("text/plain",t)' in content:
        asset.write_text(content)
        patched.append(asset.name)
html = INDEX_HTML.read_text()
for name in ['index-CNlFECW2.js','vendor-query-DXFmKafw.js','vendor-react-BuboTVMM.js','vendor-ui-o8MULjCw.js','vendor-charts-CVDWAzEs.js','index-BDp3hZk-.css']:
    html = re.sub(rf'(/assets/{re.escape(name)})(\?[^\"]*)?"', rf'\1"', html)
INDEX_HTML.write_text(html)
print('patched assets:', ', '.join(sorted(set(patched))))
print('cache tag removed for consistent module URLs')


# SAFE_FEATURES_REAPPLY_20260505
ACCOUNT_GRID_OLD = 'function _E({accounts:t,onAction:a}){const l=E.useMemo(()=>Tc(t),[t]);return t.length===0?i.jsx(hr,{icon:nS,title:"No accounts connected yet",description:"Import or authenticate an account to get started."}):i.jsx("div",{"data-testid":"dashboard-account-cards",className:"grid gap-4 overflow-y-auto pr-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden sm:grid-cols-2 lg:grid-cols-3",style:{maxHeight:`calc(${M0} * ${SE}rem + ${(M0-1)*NE}rem)`},children:t.map((o,u)=>i.jsx("div",{className:"animate-fade-in-up",style:{animationDelay:`${u*75}ms`},children:i.jsx(wE,{account:o,showAccountId:l.has(o.accountId),onAction:a})},o.accountId))})}'
ACCOUNT_GRID_NEW = 'function _E({accounts:t,onAction:a}){const l=E.useMemo(()=>Tc(t),[t]),o=[...t].sort((u,f)=>{const m=[u.usage?.primaryRemainingPercent,u.usage?.secondaryRemainingPercent].filter(v=>typeof v==="number"),p=[f.usage?.primaryRemainingPercent,f.usage?.secondaryRemainingPercent].filter(v=>typeof v==="number"),y=m.length?m.reduce((v,h)=>v+h,0)/m.length:0,g=p.length?p.reduce((v,h)=>v+h,0)/p.length:0;if(g!==y)return g-y;const b=u.usage?.secondaryRemainingPercent??-1,x=f.usage?.secondaryRemainingPercent??-1;if(x!==b)return x-b;const w=u.usage?.primaryRemainingPercent??-1,j=f.usage?.primaryRemainingPercent??-1;if(j!==w)return j-w;return(u.displayName||u.email||u.accountId).localeCompare(f.displayName||f.email||f.accountId)});return t.length===0?i.jsx(hr,{icon:nS,title:"No accounts connected yet",description:"Import or authenticate an account to get started."}):i.jsx("div",{"data-testid":"dashboard-account-cards",className:"grid gap-4 sm:grid-cols-2 lg:grid-cols-3",children:o.map((u,f)=>i.jsx("div",{className:"animate-fade-in-up",style:{animationDelay:`${f*75}ms`},children:i.jsx(wE,{account:u,showAccountId:l.has(u.accountId),onAction:a})},u.accountId))})}'

DASHBOARD_OLD = 'i.jsx(IE,{primaryItems:ee.primaryUsageItems,secondaryItems:ee.secondaryUsageItems,primaryTotal:L?.summary.primaryWindow.capacityCredits??0,secondaryTotal:L?.summary.secondaryWindow?.capacityCredits??0,primaryCenterValue:ee.primaryTotal,secondaryCenterValue:ee.secondaryTotal,safeLinePrimary:ee.safeLinePrimary,safeLineSecondary:ee.safeLineSecondary}),i.jsxs("section",{className:"space-y-4",children:[i.jsxs("div",{className:"flex items-center gap-3",children:[i.jsx("h2",{className:"text-[13px] font-medium uppercase tracking-wider text-muted-foreground",children:"Accounts"}),i.jsx("div",{className:"h-px flex-1 bg-border"})]}),i.jsx(_E,{accounts:L?.accounts??[],onAction:$})]})'
DASHBOARD_NEW = 'i.jsx(IE,{primaryItems:ee.primaryUsageItems,secondaryItems:ee.secondaryUsageItems,primaryTotal:L?.summary.primaryWindow.capacityCredits??0,secondaryTotal:L?.summary.secondaryWindow?.capacityCredits??0,primaryCenterValue:ee.primaryTotal,secondaryCenterValue:ee.secondaryTotal,safeLinePrimary:ee.safeLinePrimary,safeLineSecondary:ee.safeLineSecondary}),i.jsxs("section",{className:"space-y-4",children:[i.jsxs("div",{className:"flex items-center gap-3",children:[i.jsx("h2",{className:"text-[13px] font-medium uppercase tracking-wider text-muted-foreground",children:"Accounts"}),i.jsx("div",{className:"h-px flex-1 bg-border"})]}),i.jsx(_E,{accounts:L?.accounts??[],onAction:$})]})'

PACE_FN = 'function __codexLbDailyPacePanel({summary:t}){const a=t?.secondaryWindow??null;if(!a||!Number.isFinite(a.capacityCredits)||a.capacityCredits<=0||!Number.isFinite(a.remainingCredits))return null;const l=Math.max(0,a.capacityCredits-a.remainingCredits),o=Math.max(0,a.capacityCredits),u=Math.max(0,Math.min(100,l/o*100)),f=100/30,m=Math.min(30,Math.max(1,new Date().getDate())),p=f*(m-1),y=Math.max(0,Math.min(f,u-p)),g=Math.max(0,Math.min(100,y/f*100)),b=g>=100?"#ef4444":"#10b981";return i.jsx("section",{className:"rounded-xl border bg-card p-5",children:i.jsxs("div",{className:"flex flex-col items-center justify-center",children:[i.jsx("h3",{className:"text-sm font-semibold",children:"Today Coverage"}),i.jsx("div",{className:"mt-4 relative h-[152px] w-[152px] rounded-full",style:{background:`conic-gradient(${b} 0 ${g}%, #404040 ${g}% 100%)`},children:i.jsx("div",{className:"absolute inset-[16px] flex items-center justify-center rounded-full bg-card text-center",children:i.jsx("p",{className:"text-3xl font-semibold tabular-nums",children:`${g.toFixed(2)}%`})})})]})})}'


for asset in ASSETS_DIR.glob('*.js'):
    content = asset.read_text()
    changed = False
    if ACCOUNT_GRID_OLD in content:
        content = content.replace(ACCOUNT_GRID_OLD, ACCOUNT_GRID_NEW)
        changed = True
    if DASHBOARD_OLD in content:
        content = content.replace(DASHBOARD_OLD, DASHBOARD_NEW)
        changed = True
    marker = 'function sC({enabled:t,disabled:a=!1,onChange:l})'
    if changed:
        asset.write_text(content)
        if asset.name not in patched:
            patched.append(asset.name)
