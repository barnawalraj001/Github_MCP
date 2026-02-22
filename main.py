# main.py
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

from config import CLIENT_ID, CLIENT_SECRET
from tokens import save_token, get_token
import tools

app = FastAPI()


# -------------------------------------------------
# GitHub OAuth Login (TEST MODE)
# -------------------------------------------------
@app.get("/auth/github/login")
def github_login(request: Request, user_id: str):
    # Dynamically build the redirect URI based on the host serving the login request
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/auth/callback/github"
    
    github_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={user_id}"
        "&scope=repo read:user user:email"
    )
    return RedirectResponse(github_url)


# -------------------------------------------------
# GitHub OAuth Callback
# -------------------------------------------------
@app.get("/auth/callback/github")
def github_callback(code: str, state: str):
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
        return {"error": "GitHub OAuth failed"}

    save_token(state, access_token)

    return {
        "status": "connected",
        "user_id": state
    }


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

    # TEST MODE USER RESOLUTION
    user_id = meta.get("user_id")
    if not user_id:
        return JSONResponse(
            status_code=400,
            content={"error": "meta.user_id is required (test mode)"}
        )

    token = get_token(user_id)
    if not token:
        # Construct the auth URL dynamically based on the incoming request domain
        # If running locally this will typically be http://localhost:8000/auth/github/login?user_id=...
        # In a real deployed environment it will use the deployed hostname.
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

    # ---------------- tools/list ----------------
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "tools": tools.get_all_tool_schemas()
            }
        }

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
