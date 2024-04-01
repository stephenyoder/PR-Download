import unittest
import download_pr

def get_token(filename: str):
    try:
        with open(filename, 'r') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

class MyTestCase(unittest.TestCase):

    token = get_token("stephenyoder_token.txt")
    def test_list_user_prs_in_org_repos(self):
        prs = download_pr.list_user_prs_in_org_repos("vitahlin", "valkey-io", MyTestCase.token)
        for pr in prs:
            print(pr)
        self.assertEqual(len(prs), 3)

    def test_download_all_pull_requests(self):
        download_pr.download_all_pull_requests("vitahlin", "valkey-io", MyTestCase.token)

    def test_read_file_to_list(self):
        pr_names = download_pr.read_file_to_list("StephenPRs.txt")
        self.assertEqual(len(pr_names), 99)

if __name__ == '__main__':
    unittest.main()
