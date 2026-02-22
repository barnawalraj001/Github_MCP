from github_api import make_request
from utils.serializers import serialize_file, safe_list

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
    raw = make_request("GET", f"repos/{owner}/{repo}/contents/{path}", token, params=params)
    if isinstance(raw, dict) and "error" in raw:
        return raw        
    # GitHub often returns file contents as objects if it's a file, but lists if it's a directory
    return safe_list(raw, serialize_file)

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
        
    raw = make_request("PUT", f"repos/{owner}/{repo}/contents/{path}", token, json=json_data)
    if isinstance(raw, dict) and "error" in raw:
        return raw
    # We serialize the created file content representation here (or return empty if none)
    if "content" in raw and raw["content"]:
        return serialize_file(raw["content"])
    return {"status": "success"}

HANDLERS = {
    "github.get_file_contents": get_file_contents,
    "github.create_or_update_file": create_or_update_file
}
