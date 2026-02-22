from github_api import make_request

SCHEMAS = [
    {
        "name": "github.get_file_contents",
        "description": "Get file contents from a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string", "description": "File path in the repository"},
                "ref": {"type": "string", "description": "The name of the commit/branch/tag."}
            },
            "required": ["owner", "repo", "path"]
        }
    },
    {
        "name": "github.create_or_update_file",
        "description": "Create or update file contents",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string"},
                "message": {"type": "string", "description": "The commit message."},
                "content": {"type": "string", "description": "The new file content in Base64 encoding."},
                "sha": {"type": "string", "description": "The blob SHA of the file being replaced (required for updating)."},
                "branch": {"type": "string"}
            },
            "required": ["owner", "repo", "path", "message", "content"]
        }
    }
]

def get_file_contents(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    path = args["path"]
    params = {}
    if "ref" in args:
        params["ref"] = args["ref"]
    return make_request("GET", f"repos/{owner}/{repo}/contents/{path}", token, params=params)

def create_or_update_file(args: dict, token: str):
    owner = args["owner"]
    repo = args["repo"]
    path = args["path"]
    json_data = {
        "message": args["message"],
        "content": args["content"]
    }
    if "sha" in args:
        json_data["sha"] = args["sha"]
    if "branch" in args:
        json_data["branch"] = args["branch"]
        
    return make_request("PUT", f"repos/{owner}/{repo}/contents/{path}", token, json=json_data)

HANDLERS = {
    "github.get_file_contents": get_file_contents,
    "github.create_or_update_file": create_or_update_file
}
