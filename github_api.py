# github_api.py
import requests

BASE_URL = "https://api.github.com"

def _headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

def list_repos(token: str):
    r = requests.get(
        f"{BASE_URL}/user/repos",
        headers=_headers(token)
    )
    return r.json()

def list_issues(token: str, owner: str, repo: str):
    r = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/issues",
        headers=_headers(token)
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
