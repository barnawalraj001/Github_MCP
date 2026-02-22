from config import safe_limit
from github_api import make_request

SCHEMAS = [
    {
        "name": "github.list_issues",
        "description": "List issues of a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Max issues (max 30)"
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
    },
    {
        "name": "github.comment_on_issue",
        "description": "Comment on a GitHub issue",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "issue_number": {"type": "integer"},
                "body": {"type": "string"}
            },
            "required": ["owner", "repo", "issue_number", "body"]
        }
    },
    {
        "name": "github.close_issue",
        "description": "Close a GitHub issue",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "issue_number": {"type": "integer"}
            },
            "required": ["owner", "repo", "issue_number"]
        }
    }
]

def list_issues(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    limit = safe_limit(args.get("limit", 10))
    return make_request("GET", f"repos/{owner}/{repo}/issues", token, params={"per_page": limit})

def create_issue(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    title = args["title"]
    body = args.get("body", "")
    return make_request("POST", f"repos/{owner}/{repo}/issues", token, json={"title": title, "body": body})

def comment_on_issue(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    issue_number = args["issue_number"]
    body = args["body"]
    return make_request("POST", f"repos/{owner}/{repo}/issues/{issue_number}/comments", token, json={"body": body})

def close_issue(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    issue_number = args["issue_number"]
    return make_request("PATCH", f"repos/{owner}/{repo}/issues/{issue_number}", token, json={"state": "closed"})

HANDLERS = {
    "github.list_issues": list_issues,
    "github.create_issue": create_issue,
    "github.comment_on_issue": comment_on_issue,
    "github.close_issue": close_issue
}
