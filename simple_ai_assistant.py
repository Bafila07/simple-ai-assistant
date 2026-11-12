import json
import os
from utilities.utilities import log

from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOLS, function_name_to_function_map

load_dotenv()

# Create OpenAI client connected to Ollama
client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY")
)

# Store the conversation history
messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful AI assistant. "
            "Answer clearly and briefly."
        ),
    }
]

# Maximum number of steps the agent can take
MAX_STEPS = 5


while True:

    # 1. Get input from the user
    user_input = input("PRIYANSHU-BAFILA: ")

    # Exit the program if the user enters an exit command
    if user_input.lower() in ["exit", "bye", "quit", "end"]:
        print("Assistant: See you later!")
        break

    # 2. Add the user's message to conversation history
    messages.append({
        "role": "user",
        "content": user_input
    })

    # Track whether the agent completed successfully
    completed = False

    # 3. Ask the LLM for a response
    for step in range(MAX_STEPS):

        response = client.chat.completions.create(
            model=os.getenv("OLLAMA_MODEL"),
            messages=messages,
            tools=TOOLS
        )

        # Get the assistant's response
        assistant_message = response.choices[0].message

        # 4. Save the assistant's response to history
        messages.append(assistant_message)

        # If there are no tool calls, we have the final answer
        if not assistant_message.tool_calls:
            completed = True
            break

        log(
            f"Step {step + 1}: model requested tool calls :"
            f"{len(assistant_message.tool_calls)} tool_calls"
        )

        # 5. Execute each requested tool
        for tool_call in assistant_message.tool_calls:

            # Get the tool name requested by the model
            tool_name = tool_call.function.name

            tool_args = {}

            try:
                # Convert JSON arguments into a Python dictionary
                tool_args = json.loads(
                    tool_call.function.arguments or "{}"
                )

                log(
                    f" 🔧 Tool call  : {tool_name} "
                    f"with arguments: {tool_args}"
                )

                # Find the actual Python function for this tool
                tool_function = function_name_to_function_map.get(
                    tool_name
                )

                # Run the tool with the given arguments
                result = tool_function(**tool_args)

            except Exception as e:

                # Store the error instead of crashing the agent
                result = (
                    f"Error executing tool {tool_name}: {str(e)}"
                )

            # Show the tool's result
            log(f"   └─ 📋 Result: {result}")

            # 6. Add the tool result back to conversation history
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    # Check whether the agent completed within MAX_STEPS
    if not completed:

        fallback = (
            "Sorry, I couldn't provide a complete answer. "
            "Reached the maximum number of steps."
        )

        messages.append({
            "role": "assistant",
            "content": fallback
        })

        print("Assistant:", fallback)
        continue

    # 7. Print the final assistant response
    print("Assistant:", assistant_message.content or "")