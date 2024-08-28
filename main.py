import os
import asyncio
from swe import *
from utils.helpers import from_github, get_branch_name_from_issue, read_user_input, create_github_issue_validator
from utils.prompts import *

async def main():
    # Run the agent
    assistant_thread, llm, tools, composio_toolset = await init_swe_agent()
    repo, issue = await from_github(composio_toolset)

    assistant = await llm.beta.assistants.create(
        name="SWE agent",
        instructions=f"{GOAL}\nRepo is: {repo} and your goal is to {issue}",
        model="gpt-4o",
        tools=tools
    )

    await llm.beta.threads.messages.create(
        assistant_thread['id'],
        {
            'role': 'user',
            'content': issue
        }
    )

    stream = await llm.beta.threads.runs.create_and_poll(
        assistant_thread['id'],
        {
            'assistant_id': assistant['id'],
            'instructions': f"Repo is: {repo} and your goal is to {issue}",
            'tool_choice': "required"
        }
    )

    await composio_toolset.wait_and_handle_assistant_tool_calls(
        llm,
        stream,
        assistant_thread,
        "default"
    )

    response = await composio_toolset.execute_action("filetool_git_patch", {})

    if response.get('patch') and len(response['patch']) > 0:
        print(f"=== Generated Patch ===\n{response['patch']}", response)
        branch_name = get_branch_name_from_issue(issue)
        output = await composio_toolset.execute_action("SHELL_EXEC_COMMAND", {
            'cmd': f"cp -r {response['current_working_directory']} git_repo && "
                   f"cd git_repo && "
                   f"git config --global --add safe.directory '*' && "
                   f"git config --global user.name {os.getenv('GITHUB_USER_NAME')} && "
                   f"git config --global user.email {os.getenv('GITHUB_USER_EMAIL')} && "
                   f"git checkout -b {branch_name} && "
                   f"git commit -m 'feat: {issue}' && "
                   f"git push origin {branch_name}"
        })

        # Wait for 2 seconds
        await asyncio.sleep(2)

        print(f"Have pushed the code changes to the repo. Let's create the PR now", output)

        await composio_toolset.execute_action("GITHUB_PULLS_CREATE", {
            'owner': repo.split("/")[0],
            'repo': repo.split("/")[1],
            'head': branch_name,
            'base': "master",
            'title': f"SWE: {issue}"
        })

        print(f"Done! The PR has been created for this issue in {repo}")
    else:
        print('No output available - no patch was generated :(')

    await composio_toolset.workspace.close()

# Run the main function
asyncio.run(main())
