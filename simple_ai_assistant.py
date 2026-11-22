
# Standard library imports
import os
from types import SimpleNamespace

# Third-party imports
from dotenv import load_dotenv
from openai import OpenAI

# Local imports
from tools import TOOLS, run_tool
from utilities.utilities import log
from memory import list_chats, load_chat, save_chat

# Load environment variables from .env file
load_dotenv()

# Create OpenAI client connected to Ollama
client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY")
)

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a helpful, humble assistant for Zorvex Technologies employees. "
        "Answer general questions (programming, science, advice) from your own knowledge. "
        "Use get_current_time, get_city_weather and get_user_city only for the current time, the weather, or the user's city. "
        "For ANY question about Zorvex policies, benefits, leave, medical cover, HR, hiring, tech processes, incident reports or travel expenses, "
        "you MUST first call search_knowledge_base. "
        "Answer company questions ONLY from the text that search_knowledge_base returns. Do not use outside knowledge for company facts. "
        "After the answer, cite the source like (leave_policy.txt #3). "
        "If the returned text does not contain the answer, say exactly: I could not find this in the knowledge base. "
        "Keep answers under 100 words."
    )
}

# Store the conversation history
messages = [SYSTEM_PROMPT]

# Path to the current chat file, if any
chat_file_path = None

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
    calls = {}
    label_printed = False

    # Streaming started
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

    except KeyboardInterrupt:
        print("\nStreaming interrupted by user.")
        raise

    finally:
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


# Before starting the chat, offer the option to load a previous chat
existing_chats = list_chats()

if existing_chats:
    last_chat = existing_chats[0]

    answer = input(
        f"Do you want to load the last chat '{last_chat['title']}'? (y/n): "
    )

    if answer.lower() == "y":
        loaded_chat = load_chat(last_chat["path"])

        if loaded_chat is not None:
            messages = [SYSTEM_PROMPT] + loaded_chat["messages"]

            # Store the loaded chat file path
            chat_file_path = last_chat["path"]

            print(
                f"Loaded chat '{loaded_chat['title']}' "
                f"with {len(loaded_chat['messages'])} messages."
            )


while True:

    # 1. Get input from the user
    user_input = input("PRIYANSHU-BAFILA: ")

    # Exit the agent if the user enters an exit command
    if user_input.lower() in ["exit", "bye", "quit", "end"]:
        print("Assistant: See you later!")
        break

    # Check for chat management commands
    command = user_input.strip().lower()

    # Start a new chat
    if command == "/new":
        messages = [SYSTEM_PROMPT]
        chat_file_path = None

        print("Assistant: Started a new chat. The old one is saved automatically.")
        continue

    # List all saved chats
    if command == "/chats":
        chats = list_chats()

        if not chats:
            print("Assistant: No saved chats found.")
            continue

        print("Assistant: Saved Chats:")

        chat_number = 1

        for chat in chats:
            title = chat["title"]
            updated = chat["updated"]
            count = chat["count"]

            print(
                f"{chat_number}. {title} - {count} messages "
                f"(Last updated: {updated})"
            )
            chat_number += 1

        continue

    # Resume a previously saved chat
    if command == "/resume":
        chats = list_chats()

        if not chats:
            print("Assistant: No saved chats found.")
            continue

        chat_number = 1
        print("Assistant: Saved Chats:")

        for chat in chats:
            title = chat["title"]
            updated = chat["updated"]
            count = chat["count"]

            print(
                f"{chat_number}. {title} - {count} messages "
                f"(Last updated: {updated})"
            )
            chat_number += 1

        # Ask the user to select a chat
        choice = input("Enter the number of the chat to resume: ")
        choice = choice.strip()

        # Validate the selected chat number
        if not choice.isdigit() or not (1 <= int(choice) <= len(chats)):
            print("Invalid choice. Please enter a valid number.")
            continue

        picked_chat = chats[int(choice) - 1]
        data = load_chat(picked_chat["path"])

        if data is None:
            print("The chat could not be loaded. Please try again.")
            continue

        # Restore the selected conversation
        messages = [SYSTEM_PROMPT] + data["messages"]
        chat_file_path = picked_chat["path"]

        print(
            f"Resumed chat '{picked_chat['title']}' "
            f"with {len(data['messages'])} messages."
        )
        continue

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
        full_response, tool_calls = stream_chat(messages)

        # 4. Save the LLM response to the conversation history
        assistant_message = {
            "role": "assistant",
            "content": full_response
        }

        # Include tool calls only when requested
        if tool_calls:
            assistant_message["tool_calls"] = build_tool_calls_payload(tool_calls)

        messages.append(assistant_message)

        # If the LLM does not request a tool, this is the final answer
        if not tool_calls:
            completed = True
            break

        # Log how many tools the LLM wants to use
        log(
            f"Step {step + 1}: model requested tool calls: "
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

    # 7. Automatically save the conversation after each user turn
    # Exclude the system prompt from the saved messages
    chat_file_path = save_chat(chat_file_path, messages[1:])
