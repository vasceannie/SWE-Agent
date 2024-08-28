import os
from composio_openai import ComposioToolSet, WorkspaceType
from openai import OpenAI
from utils.prompts import BACKSTORY, DESCRIPTION, GOAL
from dotenv import load_dotenv

load_dotenv()

# Initialize tool.

composio_toolset = ComposioToolSet(workspace_config=WorkspaceType.Docker({}))

async def init_swe_agent():
    llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    tools = await composio_toolset.get_tools({
        'actions': [
            "FILETOOL",
            "FILEEDITTOOL",
            "SHELLTOOL"
        ],
        'logging_level': os.getenv('COMPOSIO_LOGGING_LEVEL', 'INFO')
    })

    # Truncate descriptions longer than 1024 characters
    tools = [tool if len(tool.get('function', {}).get('description', '')) <= 1024 else {**tool, 'function': {'description': tool['function']['description'][:1024]}} for tool in tools]

    # Replace nulls with empty arrays
    def update_null_to_empty_array(obj):
        for key, value in obj.items():
            if value is None:
                obj[key] = []
            elif isinstance(value, dict):
                update_null_to_empty_array(value)
        return obj

    tools = [update_null_to_empty_array(tool) for tool in tools]

    # Initialize assistant thread
    assistant_thread = await llm.beta.threads.create({
        'messages': [
            {
                'role': 'assistant',
                'content': f"{BACKSTORY}\n\n{GOAL}\n\n{DESCRIPTION}"
            }
        ]
    })

    return {'assistant_thread': assistant_thread, 'llm': llm, 'tools': tools, 'composio_toolset': composio_toolset}

# Assuming the environment setup
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
composio_toolset = ComposioToolSet(workspace_config=WorkspaceType.Docker({}))
