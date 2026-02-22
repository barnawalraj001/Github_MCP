import traceback
from . import profile, repos, issues, pull_requests, commits, files

MODULES = [profile, repos, issues, pull_requests, commits, files]

def get_all_tool_schemas():
    tools_schemas = []
    for m in MODULES:
        if hasattr(m, 'SCHEMAS'):
            tools_schemas.extend(m.SCHEMAS)
    return tools_schemas

def call_tool(tool_name: str, args: dict, token: str):
    for m in MODULES:
        if hasattr(m, 'HANDLERS') and tool_name in m.HANDLERS:
            try:
                return m.HANDLERS[tool_name](args, token)
            except Exception as e:
                # Can capture traceback.format_exc() here if testing mode enabled
                return {"error": f"Tool execution failed: {str(e)}"}
    return {"error": "Unknown tool"}
