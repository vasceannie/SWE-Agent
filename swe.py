from openai import OpenAI
from composio_core import OpenAIToolSet, Workspace
from prompts import BACKSTORY, DESCRIPTION, GOAL
import os

# Initialize tool.
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

composio_toolset = OpenAIToolSet(workspace_config=Workspace.Docker({}))
