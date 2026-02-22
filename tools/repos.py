from config import safe_limit
from github_api import make_request
from utils.serializers import serialize_repo, safe_list

SCHEMAS = [
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
        "name": "github.get_repo_details",
        "description": "Get details of a specific repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"}
            },
            "required": ["owner", "repo"]
        }
    },
    {
        "name": "github.list_branches",
        "description": "List branches of a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"}
            },
            "required": ["owner", "repo"]
        }
    }
]

def list_repos(args: dict, token: str):
    limit = safe_limit(args.get("limit", 10))
    raw = make_request("GET", "user/repos", token, params={"per_page": limit})
    # If error JSON is returned, raw will usually have 'error', which is not a list.
    if isinstance(raw, dict) and "error" in raw:
        return raw
    return safe_list(raw, serialize_repo)

def get_repo_details(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    raw = make_request("GET", f"repos/{owner}/{repo}", token)
    if isinstance(raw, dict) and "error" in raw:
        return raw
    return serialize_repo(raw)

def list_branches(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    return make_request("GET", f"repos/{owner}/{repo}/branches", token)

HANDLERS = {
    "github.list_repos": list_repos,
    "github.get_repo_details": get_repo_details,
    "github.list_branches": list_branches
}
