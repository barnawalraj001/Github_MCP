from github_api import make_request

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
    return make_request("GET", "user", token)

HANDLERS = {
    "github.get_me": get_me
}
