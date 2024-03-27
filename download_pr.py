import sys
import requests
from urllib.parse import urlparse
from github import Github
from github import Auth

def get_url(file, token, repo_name):
    # using an access token
    auth = Auth.Token(token)

    # First create a Github instance:

    # Public Web Github
    g = Github(auth=auth)

    # Github Enterprise with custom hostname
    # g = Github(base_url="https://{hostname}/api/v3", auth=auth)

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


def download_pull_request_diff(username, token, org, repo, pr_number, output_file):
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


def download_pull_request(org, access_token, repo_name, pr_number):

    filename = "pull_request_diff.txt"
    # GitHub API endpoint for PR diff
    url = f'https://api.github.com/repos/{org}/{repo_name}/pulls/{pr_number}'
    headers = {'Authorization': f'token {access_token}'}

    # Fetch PR diff using GitHub API
    response = requests.get(url, headers=headers)
    pr_diff = response.json()['diff_url']

    url = pr_diff
    print(url)
    response = requests.get(url, headers=headers)
    print(str(response.content))
    download_pull_request_diff(username, access_token, org, repo_name, pr_number, filename)

    print('Pull request diff saved to pull_request_diff.txt')


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python download_pr.py org access_token repo_name pr_number")
        sys.exit(1)

    username, access_token, repo_name, pr_number = sys.argv[1:]
    download_pull_request(username, access_token, repo_name, pr_number)
