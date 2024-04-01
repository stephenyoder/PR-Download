import sys
import requests
from github import Github


def read_file_to_list(file_path):
    # Initialize an empty list to store the lines
    lines_list = []

    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read each line and add it to the list
            for line in file:
                lines_list.append(line.strip())  # strip() removes leading and trailing whitespaces

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return lines_list


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
