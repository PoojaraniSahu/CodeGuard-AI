import os
from github import Github, Auth
from sqlalchemy.orm import Session
import models

def get_github_client(access_token: str) -> Github:
    auth = Auth.Token(access_token)
    return Github(auth=auth)

def fetch_user_repos(access_token: str):
    gh = get_github_client(access_token)
    repos = []
    # Fetch repositories the user has access to
    for repo in gh.get_user().get_repos(affiliation="owner,collaborator"):
        repos.append({
            "id": repo.id,
            "full_name": repo.full_name,
            "html_url": repo.html_url,
            "description": repo.description,
            "language": repo.language,
        })
    return repos

def setup_repo_webhook(access_token: str, repo_name: str, webhook_url: str):
    gh = get_github_client(access_token)
    repo = gh.get_repo(repo_name)

    # Check if webhook exists
    for hook in repo.get_hooks():
        if hook.config.get("url") == webhook_url:
            return hook.id

    # Create new webhook for Pull Requests
    config = {
        "url": webhook_url,
        "content_type": "json"
    }
    hook = repo.create_hook("web", config, ["pull_request", "push"], active=True)
    return hook.id

def get_pr_diff(access_token: str, repo_name: str, pr_number: int):
    gh = get_github_client(access_token)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # We can get files diff via the PR files API
    files_diff = []
    for file in pr.get_files():
        files_diff.append({
            "filename": file.filename,
            "status": file.status, # added, removed, modified
            "patch": file.patch, # The actual diff chunk
        })
    return files_diff, pr.title, pr.body

def post_pr_comment(access_token: str, repo_name: str, pr_number: int, body: str):
    gh = get_github_client(access_token)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)

def get_all_repo_files(access_token: str, repo_name: str):
    """Recursively fetches all relevant text/code files from the repository."""
    gh = get_github_client(access_token)
    repo = gh.get_repo(repo_name)
    
    files_content = []
    
    def process_content(contents):
        for content_file in contents:
            if content_file.type == "dir":
                # Skip massive directories or common ignorables to save API/AI quota
                if content_file.name not in [".git", "node_modules", "venv", "__pycache__", "build", "dist"]:
                    process_content(repo.get_contents(content_file.path))
            else:
                # Basic check to only grab source code / text files
                ext = content_file.path.split(".")[-1].lower() if "." in content_file.path else ""
                if ext in ["py", "js", "ts", "jsx", "tsx", "html", "css", "java", "cpp", "c", "go", "rs", "php", "rb"]:
                    try:
                        decoded_content = content_file.decoded_content.decode('utf-8')
                        files_content.append({
                            "filename": content_file.path,
                            "content": decoded_content
                        })
                    except Exception:
                        pass # Ignore binary or undecodable files

    # Get root contents and recurse
    root_contents = repo.get_contents("")
    process_content(root_contents)
    
    return files_content
