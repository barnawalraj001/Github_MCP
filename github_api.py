import requests
from config import GITHUB_API_BASE_URL

def _headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def make_request(method: str, endpoint: str, token: str, params=None, json=None):
    """
    Generic request handler for GitHub API.
    Provides centralized error handling and response parsing.
    """
    url = f"{GITHUB_API_BASE_URL}/{endpoint.lstrip('/')}"
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=_headers(token),
            params=params,
            json=json,
            timeout=10
        )
        response.raise_for_status()
        
        # Handle endpoints that return 204 No Content
        if response.status_code == 204:
            return {"status": "success"}
            
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_msg = e.response.json()
            except Exception:
                error_msg = e.response.text
        return {"error": "GitHub API failure", "details": error_msg}
