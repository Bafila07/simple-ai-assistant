# Standard library imports
import os
from types import SimpleNamespace

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
def stream_chat(history):
    """
    Stream the chat response from the model.

    Args:
        history (list): The conversation history.   

    Returns:
        tuple: A tuple containing the full response and a list of tool calls.
    """
    stream = client.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL"),
        messages=history,
        tools=TOOLS,
        stream=True,
    )

    full_response = ""
    calls={}
    label_printed = False

    #Streaming Started
    try:
        for chunk in stream:
                if not chunk.choices:
                    continue
        
                delta = chunk.choices[0].delta
        
                # Display normal text immediately
                if delta.content:
                    if not label_printed:
                        print("Assistant:    ", end="", flush=True)
                        label_printed = True
                    print(delta.content, end="", flush=True)
                    full_response += delta.content
        
        
        
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
    except KeyboardInterrupt as e:
        print("\nStreaming interrupted by user.")
        stream.close()
    if label_printed:
        print()
    return full_response, list(calls.values())

def build_tool_calls_payload(tool_calls):
    """
    Build a list of tool call payloads for the assistant's message.

    Args:
        tool_calls (list): A list of tool call objects.

    Returns:
        list: A list of tool call payloads.
    """

    payloads = []
    for tool_call in tool_calls:
        payload = {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments
            }
        }
        payloads.append(payload)
    return payloads

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
        full_response,tool_calls = stream_chat(messages)


        # 4. Save the LLM response to the conversation history
        messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "tool_calls": build_tool_calls_payload(tool_calls)
            }
        )

        # If the LLM does not request a tool, this is the final answer
        if not tool_calls:
            completed = True
            break

        # Log how many tools the LLM wants to use
        log(
            f"Step {step + 1}: model requested tool calls :"
            f"{len(tool_calls)} tool_calls"
        )

        # 5. Execute each tool requested by the LLM
        for tool_call in tool_calls:

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
