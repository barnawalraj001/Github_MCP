# github_api.py
import requests

BASE_URL = "https://api.github.com"
MAX_LIMIT = 30

def _headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

def _safe_limit(limit: int):
    try:
        return min(int(limit), MAX_LIMIT)
    except Exception:
        return 10

def get_me(token: str):
    r = requests.get(
        f"{BASE_URL}/user",
        headers=_headers(token)
    )
    return r.json()

def list_repos(token: str, limit: int = 10):
    limit = _safe_limit(limit)
    r = requests.get(
        f"{BASE_URL}/user/repos",
        headers=_headers(token),
        params={"per_page": limit}
    )
    return r.json()

def list_issues(token: str, owner: str, repo: str, limit: int = 10):
    limit = _safe_limit(limit)
    r = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/issues",
        headers=_headers(token),
        params={"per_page": limit}
    )
    return r.json()

def create_issue(token: str, owner: str, repo: str, title: str, body: str = ""):
    r = requests.post(
        f"{BASE_URL}/repos/{owner}/{repo}/issues",
        headers=_headers(token),
        json={
            "title": title,
            "body": body
        }
    )
    return r.json()
