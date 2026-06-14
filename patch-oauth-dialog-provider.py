from pathlib import Path


OAUTH_DIALOG_FILE = Path("/app/app/static/assets/oauth-dialog-BezS6EE0.js")
INDEX_FILE = Path("/app/app/static/assets/index-CNlFECW2.js")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"target snippet not found: {label}")
    return content.replace(old, new, 1)


oauth_dialog = OAUTH_DIALOG_FILE.read_text()
oauth_dialog = replace_once(
    oauth_dialog,
    """function _({open:t,state:s,onOpenChange:i,onStart:a,onComplete:c,onManualCallback:u,onReset:x}){const[d,p]=l.useState("browser"),r=O(s),f=l.useRef(!1),o=r==="browser"&&s.status==="starting";l.useEffect(()=>{r==="success"&&!f.current&&(f.current=!0,c()),r==="intro"&&(f.current=!1)},[r,c]);const m=j=>{i(j),j||(x(),p("browser"))},y=()=>{a(d)},C=()=>{a("browser")},g=()=>{x()};return e.jsx(k,{open:t,onOpenChange:m,children:e.jsxs(U,{children:[""",
    """function _({open:t,state:s,onOpenChange:i,onStart:a,onComplete:c,onManualCallback:u,onReset:x}){const[d,p]=l.useState("browser"),[P,T0]=l.useState("openai"),r=O(s),f=l.useRef(!1),o=r==="browser"&&s.status==="starting";l.useEffect(()=>{r==="success"&&!f.current&&(f.current=!0,c()),r==="intro"&&(f.current=!1)},[r,c]);const m=j=>{i(j),j||(x(),p("browser"),T0("openai"))},y=()=>{a(d,P)},C=()=>{a("browser",P)},g=()=>{x(),T0("openai")};return e.jsx(k,{open:t,onOpenChange:m,children:e.jsxs(U,{children:[""",
    "oauth dialog provider state",
)
oauth_dialog = replace_once(
    oauth_dialog,
    """r==="intro"?e.jsxs("div",{className:"space-y-2",children:[e.jsxs("button",{type:"button",onClick:()=>p("browser"),className:w("w-full cursor-pointer rounded-lg border p-3 text-left transition-colors",d==="browser"?"border-primary bg-primary/5":"hover:bg-muted/50"),children:[e.jsx("p",{className:"text-sm font-medium",children:"Browser (PKCE)"}),e.jsx("p",{className:"mt-0.5 text-xs text-muted-foreground",children:"Opens a browser window for sign-in. Recommended for most users."})]}),e.jsxs("button",{type:"button",onClick:()=>p("device"),className:w("w-full cursor-pointer rounded-lg border p-3 text-left transition-colors",d==="device"?"border-primary bg-primary/5":"hover:bg-muted/50"),children:[e.jsx("p",{className:"text-sm font-medium",children:"Device code"}),e.jsx("p",{className:"mt-0.5 text-xs text-muted-foreground",children:"Use a code on another device. Useful for headless environments."})]})]}):null,""",
    """r==="intro"?e.jsxs("div",{className:"space-y-3",children:[e.jsxs("div",{className:"space-y-2",children:[e.jsx("p",{className:"text-xs font-medium text-muted-foreground",children:"Provider"}),e.jsxs("button",{type:"button",onClick:()=>T0("openai"),className:w("w-full cursor-pointer rounded-lg border p-3 text-left transition-colors",P==="openai"?"border-primary bg-primary/5":"hover:bg-muted/50"),children:[e.jsx("p",{className:"text-sm font-medium",children:"OpenAI / ChatGPT"}),e.jsx("p",{className:"mt-0.5 text-xs text-muted-foreground",children:"Uses the current OpenAI account flow that is already active in this build."})]}),e.jsxs("button",{type:"button",onClick:()=>T0("github-copilot"),className:w("w-full cursor-pointer rounded-lg border p-3 text-left transition-colors",P==="github-copilot"?"border-primary bg-primary/5":"hover:bg-muted/50"),children:[e.jsx("p",{className:"text-sm font-medium",children:"GitHub Copilot"}),e.jsx("p",{className:"mt-0.5 text-xs text-muted-foreground",children:"Uses a separate GitHub provider path when that provider is enabled."})]})]}),e.jsxs("div",{className:"space-y-2",children:[e.jsx("p",{className:"text-xs font-medium text-muted-foreground",children:"Sign-in method"}),e.jsxs("button",{type:"button",onClick:()=>p("browser"),className:w("w-full cursor-pointer rounded-lg border p-3 text-left transition-colors",d==="browser"?"border-primary bg-primary/5":"hover:bg-muted/50"),children:[e.jsx("p",{className:"text-sm font-medium",children:"Browser (PKCE)"}),e.jsx("p",{className:"mt-0.5 text-xs text-muted-foreground",children:"Opens a browser window for sign-in. Recommended for most users."})]}),e.jsxs("button",{type:"button",onClick:()=>p("device"),className:w("w-full cursor-pointer rounded-lg border p-3 text-left transition-colors",d==="device"?"border-primary bg-primary/5":"hover:bg-muted/50"),children:[e.jsx("p",{className:"text-sm font-medium",children:"Device code"}),e.jsx("p",{className:"mt-0.5 text-xs text-muted-foreground",children:"Use a code on another device. Useful for headless environments."})]})]}),P==="github-copilot"?e.jsx("p",{className:"text-xs text-muted-foreground",children:"GitHub Copilot requires separate provider setup from the default OpenAI account flow."}):null]}):null,""",
    "oauth dialog intro provider buttons",
)
OAUTH_DIALOG_FILE.write_text(oauth_dialog)
print("patched", OAUTH_DIALOG_FILE)


index_content = INDEX_FILE.read_text()
index_content = replace_once(
    index_content,
    'nA=oe({forceMethod:B().optional()})',
    'nA=oe({forceMethod:B().optional(),provider:B().optional()})',
    "oauth start schema provider field",
)
index_content = replace_once(
    index_content,
    """y=E.useCallback(async x=>{u(),f(),a(w=>({...w,status:"starting",errorMessage:null}));try{const w=await cT({forceMethod:x}),j=pa.parse({status:"pending",method:w.method==="device"?"device":"browser",authorizationUrl:w.authorizationUrl,callbackUrl:w.callbackUrl,verificationUrl:w.verificationUrl,userCode:w.userCode,deviceAuthId:w.deviceAuthId,intervalSeconds:w.intervalSeconds,expiresInSeconds:w.expiresInSeconds,errorMessage:null});return a(j),j.method==="device"&&j.deviceAuthId&&j.userCode&&await _0({deviceAuthId:j.deviceAuthId,userCode:j.userCode}),j}catch(w){const j=w instanceof Error?w.message:"Failed to start OAuth";throw a(O=>pa.parse({...O,status:"error",errorMessage:j})),w}},""",
    """y=E.useCallback(async(x,W)=>{u(),f(),a(w=>({...w,status:"starting",errorMessage:null}));try{const j=await cT({forceMethod:x,provider:W??"openai"}),O=pa.parse({status:"pending",method:j.method==="device"?"device":"browser",authorizationUrl:j.authorizationUrl,callbackUrl:j.callbackUrl,verificationUrl:j.verificationUrl,userCode:j.userCode,deviceAuthId:j.deviceAuthId,intervalSeconds:j.intervalSeconds,expiresInSeconds:j.expiresInSeconds,errorMessage:null});return a(O),O.method==="device"&&O.deviceAuthId&&O.userCode&&await _0({deviceAuthId:O.deviceAuthId,userCode:O.userCode}),O}catch(j){const O=j instanceof Error?j.message:"Failed to start OAuth";throw a(P=>pa.parse({...P,status:"error",errorMessage:O})),j}},""",
    "oauth start mutation provider payload",
)
index_content = replace_once(
    index_content,
    'onStart:async W=>{await p.start(W)}',
    'onStart:async(W,P)=>{await p.start(W,P)}',
    "oauth dialog onStart provider arg",
)
INDEX_FILE.write_text(index_content)
print("patched", INDEX_FILE)
