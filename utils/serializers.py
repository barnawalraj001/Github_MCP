def safe_list(data, serializer):
    """
    Apply a serializer safely to either a single object or a list of objects.
    """
    if data is None:
        return None
    if not isinstance(data, list):
        return serializer(data)
    return [serializer(item) for item in data]

def serialize_user(user: dict) -> dict:
    if not isinstance(user, dict):
        return user
        
    return {
        "id": user.get("id"),
        "login": user.get("login"),
        "name": user.get("name"),
        "url": user.get("html_url") or user.get("url")
    }

def serialize_repo(repo: dict) -> dict:
    if not isinstance(repo, dict):
        return repo
        
    return {
        "id": repo.get("id"),
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "private": repo.get("private"),
        "url": repo.get("html_url") or repo.get("url"),
        "default_branch": repo.get("default_branch"),
        "language": repo.get("language"),
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "updated_at": repo.get("updated_at")
    }

def serialize_issue(issue: dict) -> dict:
    if not isinstance(issue, dict):
        return issue
        
    author = issue.get("user", {}).get("login", "")
        
    return {
        "id": issue.get("id"),
        "number": issue.get("number"),
        "title": issue.get("title"),
        "state": issue.get("state"),
        "url": issue.get("html_url") or issue.get("url"),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "comments": issue.get("comments", 0),
        "author": author,
        "body": issue.get("body", "")
    }

def serialize_pull_request(pr: dict) -> dict:
    if not isinstance(pr, dict):
        return pr
        
    author = pr.get("user", {}).get("login", "")
        
    return {
        "id": pr.get("id"),
        "number": pr.get("number"),
        "title": pr.get("title"),
        "state": pr.get("state"),
        "url": pr.get("html_url") or pr.get("url"),
        "created_at": pr.get("created_at"),
        "merged": pr.get("merged", False),
        "author": author
    }

def serialize_commit(commit_obj: dict) -> dict:
    if not isinstance(commit_obj, dict):
        return commit_obj
        
    commit_data = commit_obj.get("commit", {})
    author_info = commit_data.get("author", {})
    
    # Sometimes author is tied to "author" top-level node for GitHub user
    github_author = commit_obj.get("author", {}) or {}
    author_login = github_author.get("login") or author_info.get("name", "")
    
    return {
        "sha": commit_obj.get("sha"),
        "message": commit_data.get("message", ""),
        "author": author_login,
        "date": author_info.get("date", ""),
        "url": commit_obj.get("html_url") or commit_obj.get("url")
    }

def serialize_file(file_obj: dict) -> dict:
    if not isinstance(file_obj, dict):
        return file_obj
        
    content = file_obj.get("content", "")
    if content and len(content) > 5000:
        content = content[:5000] + "\n...[Content Truncated]..."
        
    return {
        "name": file_obj.get("name"),
        "path": file_obj.get("path"),
        "size": file_obj.get("size"),
        "content": content,
        "encoding": file_obj.get("encoding")
    }
