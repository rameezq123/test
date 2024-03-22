"""
This script is used to interact with GitHub's API to perform various operations such as creating a repository,
renaming a branch, updating the default branch, adding collaborators and teams to a repository, adding a .gitignore file,
and protecting a branch.
"""

import requests
import json
import argparse
import os
import base64

# Parse command line arguments
parser = argparse.ArgumentParser(description="GitHub Repo Creation Utility",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--name", help="Repository Name")
parser.add_argument("-o", "--organization", help="Organization Name")
parser.add_argument("-d", "--description",
                    help="Repository Description", default="")
parser.add_argument("-b", "--defbranch", help="Default Branch", default="main")
args = parser.parse_args()
config = vars(args)
print(f"Arguments Passed in: {config}")


class Repo:
    """
    This class represents a GitHub repository. It includes methods for creating the repository, renaming a branch,
    updating the default branch, adding collaborators and teams, adding a .gitignore file, and protecting a branch.
    """

    # Class attributes
    auth_headers = {
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(os.getenv("GITHUB_TOKEN"))
    }

    def __init__(self, org, repo_name):
        """
        Initialize a Repo object with the given organization and repository name.
        """

        self.org = org
        self.repo_name = "repo-{}".format(repo_name)

    # Create Repo Method
    def create_repo(self, repo_description):
        """
        Create a new repository with the given description.
        """

        repo_creation_config = {
            "name": self.repo_name,
            "description": f"{repo_description}",
            "homepage": "https://github.com",
            "private": True,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
            "auto_init": True
        }

        r = requests.post(
            "https://api.github.com/user/repos",
            headers=self.auth_headers,
            data=json.dumps(repo_creation_config)
        )

        res_dict = json.loads(r.text)

        if r.status_code == 201:
            print(f"Created: {res_dict['html_url']}")
        else:
            print(f'Create repo error Message: {res_dict["message"]}')

        return repo_creation_config["name"]

    def rename_branch(self, old_name, new_name):
        """
        Rename a branch in the repository from old_name to new_name.
        """

        r = requests.post(
            "https://api.github.com/repos/{}/{}/branches/{}/rename".format(
                self.org, self.repo_name, old_name),
            headers=self.auth_headers,
            data=json.dumps({"new_name": new_name})
        )

        res_dict = json.loads(r.text)

        if r.status_code == 201:
            print("Default branch is now: {}".format(new_name))
        else:
            print('Error Message: {}'.format(res_dict["message"]))

    def update_default_branch(self, default_branch):
        """
        Update the default branch of the repository to the given branch.
        """

        r = requests.patch(
            "https://api.github.com/repos/{}/{}".format(
                self.org, self.repo_name),
            headers=self.auth_headers,
            data=json.dumps({"default_branch": default_branch})
        )

        res_dict = json.loads(r.text)

        if r.status_code == 200:
            print("Default branch is now: {}".format(default_branch))
        else:
            print('Error Message: {}'.format(res_dict["message"]))

    def add_repo_collaborator(self, username, permission):
        """
        Add a collaborator with the given username and permission to the repository.
        """

        r = requests.put(
            "https://api.github.com/repos/{}/{}/collaborators/{}".format(
                self.org, self.repo_name, username),
            headers=self.auth_headers,
            data=json.dumps({"permission": permission})
        )

        if r.status_code == 200:
            print("{} added to repo with permission: {}".format(
                username, permission))
        elif r.status_code == 204:
            print("{} already has {} permissions".format(username, permission))
        else:
            res_dict = json.loads(r.text)
            print('Error Message: {}'.format(res_dict["message"]))

    def add_repo_team(self, team_name, permission):
        """
        Add a team with the given name and permission to the repository.
        """

        r = requests.put(
            "https://api.github.com/orgs/{0}/teams/{1}/repos/{0}/{2}".format(
                self.org, team_name, self.repo_name),
            headers=self.auth_headers,
            data=json.dumps({"permission": permission})
        )

        if r.status_code == 204:
            print("{} team added as {}".format(team_name, permission))
        else:
            res_dict = json.loads(r.text)
            print('Error Message: {}'.format(res_dict["message"]))

    def add_gitignore_to_repo(self):
        """
        Add a .gitignore file to the repository.
        """

        content = ".terraform\n.terraform.tfstate\n*.tfstate*\n*.zip*\n.idea\n.secret.auto.tfvars"
        encoded_content = base64.b64encode(content.encode()).decode()

        r = requests.put(
            "https://api.github.com/repos/{}/{}/contents/.gitignore".format(
                self.org, self.repo_name),
            headers=self.auth_headers,
            json={
                "message": ".gitignore file added",
                "content":  encoded_content
            }
        )

        if r.status_code == 201:
            print("{} .gitignore file added {}")
        else:
            res_dict = json.loads(r.text)
            print('Error Message: {}'.format(res_dict["message"]))

    def protect_branch(
            self,
            branch_name,
            pr_dismissal_teams=None,
            pr_dismissal_users=None,
            pr_bypass_teams=None,
            pr_bypass_users=None,
            restriction_bypass_teams=None,
            restriction_bypass_users=None):
        """
        Protect a branch in the repository with the given settings.
        """

        if pr_dismissal_teams is None:
            pr_dismissal_teams = []
        if pr_dismissal_users is None:
            pr_dismissal_users = []
        if pr_bypass_teams is None:
            pr_bypass_teams = []
        if pr_bypass_users is None:
            pr_bypass_users = []
        if restriction_bypass_teams is None:
            restriction_bypass_teams = []
        if restriction_bypass_users is None:
            restriction_bypass_users = []

        branch_protection_config = {
            "required_status_checks": None,
            "enforce_admins": True,
            "required_pull_request_reviews": {
                "dismissal_restrictions": {
                    "teams": pr_dismissal_teams,
                    "users": pr_dismissal_users
                },
                "dismiss_stale_reviews": True,
                "required_approving_review_count": 1,
                "require_last_push_approval": True,
                "bypass_pull_request_allowances": {
                    "teams": pr_bypass_teams,
                    "users": pr_bypass_users
                },
            },
            "restrictions": {
                "teams": restriction_bypass_teams,
                "users": restriction_bypass_users
            },
            "allow_force_pushes": False,
            "allow_deletions": False,
        }

        r = requests.put(
            "https://api.github.com/repos/{}/{}/branches/{}/protection".format(
                self.org, self.repo_name, branch_name),
            headers=self.auth_headers,
            data=json.dumps(branch_protection_config)
        )

        if r.status_code == 200:
            print("{} branch is now protected".format(branch_name))
        else:
            res_dict = json.loads(r.text)
            print('Error Message: {}'.format(res_dict["message"]))


if __name__ == '__main__':
    if "GITHUB_TOKEN" not in os.environ:
        print("GITHUB TOKEN not in environment")
        exit(1)
    elif args.name is None:
        print("Repo Name required")
        exit(1)
    else:
        print("Creating Repo")
        repo = Repo(args.organization, args.name)
        repo.create_repo("This is a description of the repo")
        if args.defbranch != "main":
            print("Updating Default Branch")
            repo.rename_branch("main", args.defbranch)
        print("Updating Collaborators")
        # repo.add_repo_collaborator("admin-user", "admin")
        # repo.add_repo_team("maintain-user", "maintain")
        # repo.add_repo_team("admin-user", "admin")
        print("Updating Default Branch Protection")
        repo.protect_branch(
            args.defbranch,
            pr_dismissal_teams=["admin-user"],
            pr_bypass_teams=["admin-user"],
            restriction_bypass_teams=["admin-user"]
        )
        repo.add_gitignore_to_repo()
