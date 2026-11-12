# Standard library imports
import os

# Third-party imports
from dotenv import load_dotenv
from openai import OpenAI

# Local imports
from tools import TOOLS, run_tool
from utilities.utilities import log

# Load environment variables from .env file
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
            "Answer general questions using your own knowledge. "
            "Use tools only when they are relevant or necessary. "
            "Do not refuse a question simply because no tool is available. "
            "Answer clearly and briefly."
        ),
    }
]

# Maximum number of agent steps allowed
MAX_STEPS = 5


while True:

    # 1. Get input from the user
    user_input = input("PRIYANSHU-BAFILA: ")

    # Exit the agent if the user enters an exit command
    if user_input.lower() in ["exit", "bye", "quit", "end"]:
        print("Assistant: See you later!")
        break

    # 2. Add the user's message to the conversation history
    messages.append({
        "role": "user",
        "content": user_input
    })

    # Track whether the agent reached a final answer
    completed = False

    # 3. Run the agent for a maximum of MAX_STEPS
    for step in range(MAX_STEPS):

        # Send the conversation and available tools to the LLM
        response = client.chat.completions.create(
            model=os.getenv("OLLAMA_MODEL"),
            messages=messages,
            tools=TOOLS
        )

        # Get the LLM's response
        assistant_message = response.choices[0].message

        # 4. Save the LLM response to the conversation history
        messages.append(assistant_message)

        # If the LLM does not request a tool, this is the final answer
        if not assistant_message.tool_calls:
            completed = True
            break

        # Log how many tools the LLM wants to use
        log(
            f"Step {step + 1}: model requested tool calls :"
            f"{len(assistant_message.tool_calls)} tool_calls"
        )

        # 5. Execute each tool requested by the LLM
        for tool_call in assistant_message.tool_calls:

            # Send the tool call to the tool executor
            result = run_tool(tool_call)

            # 6. Add the tool result back to the conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    # Check if the agent failed to finish within MAX_STEPS
    if not completed:

        # Give a fallback response when the step limit is reached
        fallback = (
            "Sorry, I couldn't provide a complete answer. "
            "Reached the maximum number of steps."
        )

        # Save the fallback response to the conversation
        messages.append({
            "role": "assistant",
            "content": fallback
        })

        print("Assistant:", fallback)
        continue

    # 7. Print the final answer from the LLM
    print("Assistant:", assistant_message.content or "")