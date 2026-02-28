# main.py
import os
import json
import secrets
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import CLIENT_ID, CLIENT_SECRET
from tokens import save_token, get_token, redis_client, delete_token
import tools

app = FastAPI()

FRONTEND_URLS_ENV = os.environ.get("FRONTEND_URLS", "http://localhost:3000")
FRONTEND_URLS = [url.strip() for url in FRONTEND_URLS_ENV.split(",") if url.strip()]
if not FRONTEND_URLS:
    FRONTEND_URLS = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_PREFIX = "oauth_state"

def _state_key(state: str) -> str:
    return f"{STATE_PREFIX}:{state}"


# -------------------------------------------------
# GitHub OAuth Login (TEST MODE)
# -------------------------------------------------
@app.get("/auth/github/login")
def github_login(request: Request, user_id: str = "default", redirect_origin: str = None):
    # Validate redirect_origin strictly
    if not redirect_origin:
        raise HTTPException(status_code=400, detail="redirect_origin is required")

    if redirect_origin not in FRONTEND_URLS:
        raise HTTPException(status_code=400, detail="Invalid redirect_origin")

    state = secrets.token_urlsafe(16)
    
    # Store state in Redis
    state_data = {
        "user_id": user_id,
        "redirect_origin": redirect_origin
    }
    redis_client.setex(_state_key(state), 300, json.dumps(state_data))

    # Dynamically build the redirect URI based on the host serving the login request
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/auth/callback/github"
    
    github_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        "&scope=repo read:user user:email"
    )
    return RedirectResponse(github_url)


# -------------------------------------------------
# GitHub OAuth Callback
# -------------------------------------------------
@app.get("/auth/callback/github")
def github_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    # Default fallback
    redirect_origin = FRONTEND_URLS[0]

    if not code or not state:
        return RedirectResponse(f"{redirect_origin}/integrations/callback?service=github&status=error")

    state_data_str = redis_client.get(_state_key(state))
    if not state_data_str:
        return RedirectResponse(f"{redirect_origin}/integrations/callback?service=github&status=error")

    try:
        state_data = json.loads(state_data_str)
        user_id = state_data.get("user_id", "default")
        redirect_origin = state_data.get("redirect_origin", FRONTEND_URLS[0])
    except Exception:
        return RedirectResponse(f"{redirect_origin}/integrations/callback?service=github&status=error")

    if redirect_origin not in FRONTEND_URLS:
        redirect_origin = FRONTEND_URLS[0]

    try:
        token_res = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
            },
        ).json()

        access_token = token_res.get("access_token")
        if not access_token:
            return RedirectResponse(f"{redirect_origin}/integrations/callback?service=github&status=error")

        save_token(user_id, access_token)
        
        # Cleanup state
        redis_client.delete(_state_key(state))

        return RedirectResponse(f"{redirect_origin}/integrations/callback?service=github&status=success")
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return RedirectResponse(f"{redirect_origin}/integrations/callback?service=github&status=error")


@app.post("/auth/disconnect")
async def disconnect_github(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})
        
    user_id = payload.get("user_id")
    if not user_id:
        return JSONResponse(status_code=400, content={"error": "Missing user_id"})

    delete_token(user_id)
    return {"success": True, "service": "github"}


# -------------------------------------------------
# MCP Endpoint
# -------------------------------------------------
@app.post("/mcp")
async def mcp_handler(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON body"}
        )

    method = body.get("method")
    id_ = body.get("id")
    params = body.get("params", {})
    meta = body.get("meta", {})

    # ---------------- tools/list (no auth required) ----------------
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "tools": tools.get_all_tool_schemas()
            }
        }

    # TEST MODE USER RESOLUTION (required for all other methods)
    user_id = meta.get("user_id")
    if not user_id:
        return JSONResponse(
            status_code=400,
            content={"error": "meta.user_id is required (test mode)"}
        )

    token = get_token(user_id)
    if not token:
        base_url = str(request.base_url).rstrip("/")
        auth_url = f"{base_url}/auth/github/login?user_id={user_id}"
        return JSONResponse(
            status_code=401,
            content={
                "error": f"GitHub not connected for user_id={user_id}",
                "auth_url": auth_url,
                "message": f"Please visit {auth_url} to connect your GitHub account."
            }
        )

    # ---------------- tools/call ----------------
    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if not tool_name:
            return JSONResponse(
                status_code=400,
                content={"error": "Tool name is required in arguments"}
            )

        result = tools.call_tool(tool_name, args, token)

        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": result
        }

    return JSONResponse(
        status_code=400,
        content={"error": "Invalid MCP method"}
    )
