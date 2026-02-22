from github_api import make_request
from utils.serializers import serialize_user

SCHEMAS = [
    {
        "name": "github.get_me",
        "description": "Get connected GitHub user profile",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

def get_me(args: dict, token: str):
    raw = make_request("GET", "user", token)
    if isinstance(raw, dict) and "error" in raw:
        return raw        
    return serialize_user(raw)

HANDLERS = {
    "github.get_me": get_me
}
