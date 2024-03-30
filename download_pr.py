import sys
import requests
from urllib.parse import urlparse
from github import Github
from github import Auth


def list_user_pull_requests(username, access_token):
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get the list of user's repositories
    repositories_url = f'https://api.github.com/users/{username}/repos'
    repositories_response = requests.get(repositories_url, headers=headers)

    if repositories_response.status_code != 200:
        print(f'Error getting repositories: {repositories_response.status_code}')
        return

    repositories = repositories_response.json()

    # Iterate through each repository and get its pull requests
    user_pull_requests = []
    for repo in repositories:
        repo_name = repo['name']
        repo_pulls_url = f'https://api.github.com/repos/{username}/{repo_name}/pulls'
        pulls_response = requests.get(repo_pulls_url, headers=headers)

        if pulls_response.status_code == 200:
            pulls = pulls_response.json()
            for pull in pulls:
                if pull['user']['login'] == username:
                    user_pull_requests.append({
                        'repo_name': repo_name,
                        'title': pull['title'],
                        'url': pull['html_url']
                    })
        else:
            print(f'Error getting pull requests for {repo_name}: {pulls_response.status_code}')

    return user_pull_requests

def list_user_prs(username, user_x):
    # Initialize the GitHub API client
    g = Github()

    try:
        # Get the target user
        target_user = g.get_user(username)

        # Iterate through the repositories of the target user
        for repo in target_user.get_repos():
            # Get all pull requests in the repository
            prs = repo.get_pulls(state='all')

            # Iterate through the pull requests to find PRs created by user_x
            for pr in prs:
                if pr.user.login == user_x:
                    print(f'Repo: {repo.full_name}, PR: {pr.number}, Title: {pr.title}, Created by: {pr.user.login}')
    except Exception as e:
        print(f'Error: {e}')

def list_user_prs_in_org_repos(username, organization_name, access_token):
    # Initialize the GitHub API client
    g = Github(access_token)

    # Get the organization by name
    org = g.get_organization(organization_name)

    # Get all repositories in the organization
    org_repos = org.get_repos()

    # List to store PRs created by the user
    user_prs = []

    # Iterate through each repository
    for repo in org_repos:
        # Get all pull requests in the repository
        prs = repo.get_pulls(state='all')

        # Iterate through each pull request
        for pr in prs:
            # Check if the PR was created by the specified user
            if pr.user.login == username:
                user_prs.append({
                    'repo_name': repo.name,
                    'pr_number': pr.number,
                    'pr_title': pr.title,
                    'pr_url': pr.html_url
                })

    return user_prs


def get_url(file, token, repo_name):
    # using an access token
    auth = Auth.Token(token)

    # First create a Github instance:

    # Public Web Github
    g = Github(auth=auth)

    # Github Enterprise with custom hostname
    # g = Github(base_url="https://{hostname}/api/v3", auth=auth)

    # repos = g.get_organization(repo_name).get_repos().
    # Then play with your Github objects:
    repo = g.get_repo("stephenyoder/" + repo_name)
    pull = repo.get_pull(1)
    print(str(pull.diff_url))

    # To close connections after use
    g.close()


def download_github_url(url, username, access_token, output_file):
    # Parse the URL to get the repository owner and name
    parsed_url = urlparse(url)
    parts = parsed_url.path.split('/')
    repo_owner = parts[1]
    repo_name = parts[2]

    # Prepare the headers for authentication
    headers = {'Authorization': f'token {access_token}'}

    # Make a GET request to the GitHub URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the response content to the output file
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f'Content downloaded and saved to {output_file}')
    else:
        print(f'Error downloading content. Status code: {response.status_code}')


def download_pull_request_diff(token, org, repo, pr_number, output_file):
    url = f'https://{token}:x-oauth-basic@api.github.com/repos/{org}/{repo}/pulls/{pr_number}'
    headers = {'Accept': 'application/vnd.github.v3.diff'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Print or save the response content (pull request diff)
        with open(output_file, 'w') as file:
            file.write(response.text)
    else:
        print(f'Error: the personal access token must be a fine-grained token\
         with Contents and Pull Requests read access. {response.status_code} - {response.text}')


def download_pull_request(org, access_token, repo_name, pr_number, username):
    filename = "pull_request_" + repo_name + "_" + str(pr_number) + "_diff.txt"
    # GitHub API endpoint for PR diff
    url = f'https://api.github.com/repos/{org}/{repo_name}/pulls/{pr_number}'
    headers = {'Authorization': f'token {access_token}'}

    # Fetch PR diff using GitHub API
    response = requests.get(url, headers=headers)
    pr_diff = response.json()['diff_url']

    url = pr_diff
    # print(url)
    response = requests.get(url, headers=headers)
    # print(str(response.content))
    download_pull_request_diff(access_token, org, repo_name, pr_number, filename)

    print('Pull request diff saved')

def download_all_pull_requests(username: str, organization: str, access_token: str):
    prs = list_user_prs_in_org_repos(username, organization, access_token)
    for pr in prs:
        download_pull_request(organization, access_token, pr['repo_name'], pr['pr_number'], username)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python download_pr.py username org access_token")
        sys.exit(1)

    username, organization, access_token = sys.argv[1:]
    download_all_pull_requests(username, organization, access_token)
