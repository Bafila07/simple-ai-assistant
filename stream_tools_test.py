# Standard library imports
import os
from types import SimpleNamespace

# Third-party imports
from dotenv import load_dotenv
from openai import OpenAI

# Local imports
from tools import TOOLS, run_tool

load_dotenv()

# Create the OpenAI client
client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
)

# Store the conversation
messages = [
    {
        "role": "user",
        "content": "What is the weather in Pune?",
    }
]

# Request a streamed response from the model
stream = client.chat.completions.create(
    model=os.getenv("OLLAMA_MODEL"),
    messages=messages,
    tools=TOOLS,
    stream=True,
)

# Store tool-call fragments while they arrive
calls = {}

# Read the streamed response
for chunk in stream:
    if not chunk.choices:
        continue

    delta = chunk.choices[0].delta

    # Display normal text immediately
    if delta.content:
        print(delta.content, end="", flush=True)

    # Collect streamed tool-call fragments
    for tool_call in delta.tool_calls or []:
        index = tool_call.index

        # Create a new tool call when its first fragment arrives
        call = calls.setdefault(
            index,
            SimpleNamespace(
                id="",
                function=SimpleNamespace(
                    name="",
                    arguments="",
                ),
            ),
        )

        # Combine the streamed fragments
        if tool_call.id:
            call.id = tool_call.id

        if tool_call.function:
            if tool_call.function.name:
                call.function.name += tool_call.function.name

            if tool_call.function.arguments:
                call.function.arguments += tool_call.function.arguments

print()

# Process tool calls in their correct index order
for index in sorted(calls):
    tool_call = calls[index]

    print(f"Calling tool: {tool_call.function.name}")

    # Execute the complete tool call
    result = run_tool(tool_call)

    print(f"Tool result: {result}")