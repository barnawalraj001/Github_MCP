from config import safe_limit
from github_api import make_request
from utils.serializers import serialize_commit, safe_list

SCHEMAS = [
    {
        "name": "github.list_commits",
        "description": "List commits of a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Max commits (max 30)"
                }
            },
            "required": ["owner", "repo"]
        }
    },
    {
        "name": "github.get_commit",
        "description": "Get a specific commit",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "ref": {"type": "string", "description": "The commit reference or SHA"}
            },
            "required": ["owner", "repo", "ref"]
        }
    }
]

def list_commits(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    limit = safe_limit(args.get("limit", 10))
    raw = make_request("GET", f"repos/{owner}/{repo}/commits", token, params={"per_page": limit})
    if isinstance(raw, dict) and "error" in raw:
        return raw
    return safe_list(raw, serialize_commit)

def get_commit(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    ref = args["ref"]
    raw = make_request("GET", f"repos/{owner}/{repo}/commits/{ref}", token)
    if isinstance(raw, dict) and "error" in raw:
        return raw
    return serialize_commit(raw)

HANDLERS = {
    "github.list_commits": list_commits,
    "github.get_commit": get_commit
}
