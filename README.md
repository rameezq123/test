This repository contains a Python script that creates a new GitHub repository when triggered, using the GitHub API.

## Prerequisites

You need to have a GitHub Personal Access Token (PAT) with the necessary permissions to create repositories. This token should be stored in a secret in your GitHub repository named `GH_TOKEN`.

## Running the Python script

This Python script (main.py) is set up to run manually through the GitHub Actions tab in your repository. When you run the action, you will be prompted to enter the following information:

- Repository Name
- Organisation Name (or User Name)
- Repository Description (optional)
- Default Branch (optional)

## Example

To run the action, navigate to the Actions tab in your repository, select the "Create Repository" workflow, and click "Run workflow". Enter the required information and click "Run workflow" again.
