---
description: Instructions for using GitHub tools to interact with repositories, issues, PRs, and files.
name: GitHub MCP Skill
---

# GitHub Tool Usage Guide

You are equipped with tools to interact with GitHub via the GitHub MCP (Model Context Protocol). This document provides architectural context and guidelines for the LLM agent on how to reason about which tool to call and when.

## Available Tool Domains

The GitHub MCP exposes various operations categorized into the following domains based on the backend implementation:
- **Files (`files.py`)**: Managing repository files.
- **Repositories (`repos.py`)**: Managing repository metadata and operations.
- **Issues (`issues.py`)**: Creating, reading, and managing issues.
- **Pull Requests (`pull_requests.py`)**: Creating and reviewing PRs.
- **Commits (`commits.py`)**: Getting history and commit details.
- **Profile (`profile.py`)**: Viewing user profile information.

## How to Decide Which Tool to Call

When a user asks you to interact with GitHub, use the following reasoning process:

### 1. Identify the Objective
Determine what the user wants to achieve:
- **Reading Code/Text**: Use file-reading tools.
- **Modifying Code/Text**: Use file-writing tools.
- **Task Management**: Use issue tools.
- **Code Review/Merging**: Use pull request tools.

### 2. Select the Specific Tool
Based on the objective, select the exact tool schema name (e.g., `github.get_file_contents`).
- `github.get_file_contents`: Use to read the content of a file. Requires `owner`, `repo`, and `path`.
- `github.create_or_update_file`: Use to write or update a file. Requires `owner`, `repo`, `path`, `message` (commit message), and `content` (base64 encoded usually, ensure you follow the schema). If updating an existing file, you often need the `sha` from a previous read.

*(Note: Use `tools/list` or check the available MCP schemas dynamically if you need the exact names for issues, PRs, and repos).*

### 3. Parameter Resolution
Before invoking the tool, verify you have all required parameters:
- `owner`: The GitHub username or organization (e.g., `facebook`).
- `repo`: The repository name (e.g., `react`).
- If missing, check the conversational context or explicitly ask the user.

## Execution Flow Example

**User prompt**: "Update the README.md in my octocat/hello-world repo to say 'Hello Universe'."

**Agent Reasoning**:
1. The goal is to modify a file. I should look in the **Files** domain.
2. I need to use `github.get_file_contents` first to get the file's current `sha` blob (necessary for updating existing files).
3. Once I have the `sha`, I will call `github.create_or_update_file` with `owner="octocat"`, `repo="hello-world"`, `path="README.md"`, the new `content`, and the `sha`.
4. I will write a meaningful `message` like "docs: update README greeting".

## Error Handling
- **Authentication**: If you receive a 401 Unauthorized or an error indicating missing tokens, inform the user they need to log in via the application's OAuth flow (`/auth/github/login`).
- **Not Found**: If a 404 is returned when fetching a file, it means the file doesn't exist. You can directly call `github.create_or_update_file` without a `sha` to create it.
