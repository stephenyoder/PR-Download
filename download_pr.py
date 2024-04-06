import sys
import requests
import threading
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


def list_user_prs_in_org_repos(username, organization_name, access_token, MAX_THREADS: int, repos: list = None):
    # Initialize the GitHub API client
    g = Github(access_token)

    # Get the organization by name
    org = g.get_organization(organization_name)

    # Get all repositories in the organization
    org_repos = org.get_repos() if repos is None else repos

    # List to store PRs created by the user
    user_prs = []

    # Initialize the semaphore to control thread count
    semaphore = threading.Semaphore(MAX_THREADS)
    threads = list()

    # Iterate through each repository
    for repo in org_repos:
        print("repo:", repo.name)
        thread = threading.Thread(target=process_repo, args=(repo, semaphore, user_prs, username))
        thread.start()
        threads.append(thread)


    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    print("threads have finished getting PRs")

    return user_prs

def process_repo(repo, semaphore, user_prs, username):
    print("searching in repo:", repo.name)
    prs = repo.get_pulls(state='all')

    # Iterate through each pull request
    for pr in prs:
        # Check if the PR was created by the specified user
        if pr.user.login == username:
            print("found a PR by", username, "-", pr.title)
            with semaphore:
                user_prs.append({
                    'repo_name': repo.name,
                    'pr_number': pr.number,
                    'pr_title': pr.title,
                    'pr_url': pr.html_url
                })

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


def download_pull_request(org, access_token, repo_name, pr_number):
    filename = "pull_request_" + repo_name + "_" + str(pr_number) + "_diff.txt"
    print("downloading pull request:", repo_name, pr_number)
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


def download_all_pull_requests(username: str, organization: str, access_token: str, MAX_THREADS: int = 5):
    prs = list_user_prs_in_org_repos(username, organization, access_token, MAX_THREADS)

    # Initialize the semaphore to control thread count
    # semaphore = threading.Semaphore(MAX_THREADS)
    threads = list()

    # Iterate through each repository
    for pr in prs:
        if len(threads) >= MAX_THREADS:
            # Wait for threads to finish before creating new ones
            for thread in threads:
                thread.join()
            threads.clear()

        thread = threading.Thread(target=download_pull_request, args=(organization, access_token, pr['repo_name'], pr['pr_number']))
        threads.append(thread)
        thread.start()


    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    print("threads have finished downloading PRs")

    # for pr in prs:
    #     download_pull_request(organization, access_token, pr['repo_name'], pr['pr_number'], username)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python download_pr.py username org access_token max_threads")
        sys.exit(1)

    username, organization, access_token = sys.argv[1:4]
    MAX_THREADS = int(sys.argv[4]) if len(sys.argv) == 5 else 1
    print("starting program with", MAX_THREADS, "threads")
    download_all_pull_requests(username, organization, access_token, MAX_THREADS)
