# main.py
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv

from tokens import save_token, get_token
import github_api

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

app = FastAPI()


# -------------------------------------------------
# GitHub OAuth Login (TEST MODE)
# -------------------------------------------------
@app.get("/auth/github/login")
def github_login(user_id: str):
    github_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
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
    body = await request.json()

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
        return JSONResponse(
            status_code=401,
            content={"error": f"GitHub not connected for user_id={user_id}"}
        )

    # ---------------- tools/list ----------------
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "tools": [
                    {
                        "name": "github.get_me",
                        "description": "Get connected GitHub user profile",
                        "input_schema": {}
                    },
                    {
                        "name": "github.list_repos",
                        "description": "List GitHub repositories",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "default": 10,
                                    "description": "Max repositories (max 30)"
                                }
                            }
                        }
                    },
                    {
                        "name": "github.list_issues",
                        "description": "List issues of a repository",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "owner": {"type": "string"},
                                "repo": {"type": "string"},
                                "limit": {
                                    "type": "integer",
                                    "default": 10
                                }
                            },
                            "required": ["owner", "repo"]
                        }
                    },
                    {
                        "name": "github.create_issue",
                        "description": "Create a GitHub issue",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "owner": {"type": "string"},
                                "repo": {"type": "string"},
                                "title": {"type": "string"},
                                "body": {"type": "string"}
                            },
                            "required": ["owner", "repo", "title"]
                        }
                    }
                ]
            }
        }

    # ---------------- tools/call ----------------
    if method == "tools/call":
        tool = params.get("name")
        args = params.get("arguments", {})

        if tool == "github.get_me":
            result = github_api.get_me(token)

        elif tool == "github.list_repos":
            result = github_api.list_repos(
                token,
                args.get("limit", 10)
            )

        elif tool == "github.list_issues":
            result = github_api.list_issues(
                token,
                args["owner"],
                args["repo"],
                args.get("limit", 10)
            )

        elif tool == "github.create_issue":
            result = github_api.create_issue(
                token,
                args["owner"],
                args["repo"],
                args["title"],
                args.get("body", "")
            )

        else:
            return {"error": "Unknown tool"}

        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": result
        }

    return {"error": "Invalid MCP method"}
