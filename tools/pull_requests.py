from config import safe_limit
from github_api import make_request

SCHEMAS = [
    {
        "name": "github.list_pull_requests",
        "description": "List pull requests of a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "default": "open",
                    "description": "State of the pull requests to list."
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Max pull requests (max 30)"
                }
            },
            "required": ["owner", "repo"]
        }
    },
    {
        "name": "github.get_pull_request",
        "description": "Get details of a pull request",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "pull_number": {"type": "integer"}
            },
            "required": ["owner", "repo", "pull_number"]
        }
    },
    {
        "name": "github.create_pull_request",
        "description": "Create a pull request",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "title": {"type": "string"},
                "head": {"type": "string", "description": "The name of the branch where your changes are implemented."},
                "base": {"type": "string", "description": "The name of the branch you want the changes pulled into."},
                "body": {"type": "string"}
            },
            "required": ["owner", "repo", "title", "head", "base"]
        }
    },
    {
        "name": "github.comment_on_pull_request",
        "description": "Add a comment to a pull request",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "pull_number": {"type": "integer"},
                "body": {"type": "string"}
            },
            "required": ["owner", "repo", "pull_number", "body"]
        }
    },
    {
        "name": "github.merge_pull_request",
        "description": "Merge a pull request",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "pull_number": {"type": "integer"},
                "commit_title": {"type": "string"},
                "commit_message": {"type": "string"},
                "merge_method": {"type": "string", "enum": ["merge", "squash", "rebase"], "default": "merge"}
            },
            "required": ["owner", "repo", "pull_number"]
        }
    }
]

def list_pull_requests(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    limit = safe_limit(args.get("limit", 10))
    state = args.get("state", "open")
    return make_request(
        "GET", 
        f"repos/{owner}/{repo}/pulls", 
        token, 
        params={"per_page": limit, "state": state}
    )

def get_pull_request(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    pull_number = args["pull_number"]
    return make_request("GET", f"repos/{owner}/{repo}/pulls/{pull_number}", token)

def create_pull_request(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    return make_request(
        "POST", 
        f"repos/{owner}/{repo}/pulls", 
        token, 
        json={
            "title": args["title"],
            "head": args["head"],
            "base": args["base"],
            "body": args.get("body", "")
        }
    )

def comment_on_pull_request(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    pull_number = args["pull_number"]
    body = args["body"]
    return make_request(
        "POST", 
        f"repos/{owner}/{repo}/issues/{pull_number}/comments", 
        token, 
        json={"body": body}
    )

def merge_pull_request(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    pull_number = args["pull_number"]
    json_data = {}
    if "commit_title" in args:
        json_data["commit_title"] = args["commit_title"]
    if "commit_message" in args:
        json_data["commit_message"] = args["commit_message"]
    if "merge_method" in args:
        json_data["merge_method"] = args["merge_method"]
        
    return make_request(
        "PUT", 
        f"repos/{owner}/{repo}/pulls/{pull_number}/merge", 
        token, 
        json=json_data
    )

HANDLERS = {
    "github.list_pull_requests": list_pull_requests,
    "github.get_pull_request": get_pull_request,
    "github.create_pull_request": create_pull_request,
    "github.comment_on_pull_request": comment_on_pull_request,
    "github.merge_pull_request": merge_pull_request
}
