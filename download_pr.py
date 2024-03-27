import sys
from github import Github
import os

def download_pull_request(username, access_token, repo_name, pr_number):
    # GITHUB_ENTERPRISE_URL = 'https://github.yourcompany.com/api/v3'
    
    # Initialize the GitHub API client
    g = Github(access_token)

    # Get the repository
    repo = g.get_repo(f"{username}/{repo_name}")

    # Get the pull request
    pull = repo.get_pull(int(pr_number))

    # Clone the pull request's branch locally
    os.system(f"git clone {pull.head.repo.clone_url} --branch {pull.head.ref} --single-branch")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script_name.py username access_token repo_name pr_number")
        sys.exit(1)

    username, access_token, repo_name, pr_number = sys.argv[1:]
    access_token = ""
    download_pull_request(username, access_token, repo_name, pr_number)
