import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOLS, function_name_to_function_map

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY")
)

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful AI assistant. "
            "Answer clearly and briefly."
        ),
    }
]


while True:

    # 1. Get user input
    user_input = input("PRIYANSHU-BAFILA: ")

    if user_input.lower() in ["exit", "bye", "quit", "end"]:
        print("Assistant: See you later!")
        break

    # 2. Add user message
    messages.append({
        "role": "user",
        "content": user_input
    })

    # 3. Ask the LLM
    response = client.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL"),
        messages=messages,
        tools=TOOLS
    )

    assistant_message = response.choices[0].message

    # 4. Did the LLM ask for a tool?
    if assistant_message.tool_calls:

        # Save the assistant's tool request
        messages.append(assistant_message)

        # 5. Run the requested tool
        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            tool_args = json.loads(
                tool_call.function.arguments
            )

            tool_function = function_name_to_function_map[tool_name]

            result = tool_function(**tool_args)

            # 6. Save tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        # 7. Ask LLM again
        response = client.chat.completions.create(
            model=os.getenv("OLLAMA_MODEL"),
            messages=messages
        )

        assistant_message = response.choices[0].message

    # 8. Save assistant's final answer
    messages.append({
        "role": "assistant",
        "content": assistant_message.content
    })

    # 9. Print
    print("Assistant:", assistant_message.content)