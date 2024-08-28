import os
import sys
import readline
import json
from pathlib import Path
from nanoid import generate

class ComposioToolSet:
    def execute_action(self, action, params):
        # Implement your API call logic here
        pass

def read_user_input(prompt, metavar, validator):
    try:
        value = input(f"{prompt} > ")
        return validator(value)
    except Exception as e:
        print(f"Invalid value for `{metavar}`; error parsing `{value}`; {e}")
        sys.exit(1)

def create_github_issue_validator(owner, name, toolset):
    def github_issue_validator(value):
        resolved_path = Path(value).resolve()
        if resolved_path.exists():
            with open(resolved_path, 'r') as file:
                return file.read()

        if value.isdigit():
            response_data = toolset.execute_action('github_issues_get', {
                'owner': owner,
                'repo': name,
                'issue_number': int(value)
            })
            return response_data['body']

        return value
    return github_issue_validator

def from_github(toolset):
    owner = read_user_input(
        'Enter GitHub repository owner',
        'GitHub repository owner',
        lambda value: value
    )
    name = read_user_input(
        'Enter GitHub repository name',
        'GitHub repository name',
        lambda value: value
    )
    repo = f"{owner}/{name.replace(',', '')}"
    issue = read_user_input(
        'Enter the GitHub issue ID, description, or path to the file containing the description',
        'GitHub issue',
        create_github_issue_validator(owner, name, toolset)
    )
    return {'repo': repo, 'issue': issue}


def get_branch_name_from_issue(issue: str) -> str:
    return "swe/" + issue.lower().replace(" ", "-") + "-" + generate()
