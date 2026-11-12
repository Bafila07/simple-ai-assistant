# Simple AI Assistant

A small, terminal-based AI assistant built with Python, Ollama, and the OpenAI-compatible chat-completions API.

The project demonstrates how to build a tool-using AI agent that can:

- Answer general questions using the model's own knowledge.
- Retrieve the current date and time.
- Retrieve weather information for a city.
- Retrieve a configured user's saved city.
- Maintain conversation history during a session.
- Decide when to call tools and incorporate their results into a final answer.
- Stream a model response through a separate standalone example.

This is an educational project focused on the basic agent loop: **receive a message, ask the model what to do, execute requested tools, return tool results, and produce a final answer**.

## Features

### Conversational terminal interface

The main assistant runs in an interactive terminal session. User messages are sent to the configured model, and the resulting answer is printed back to the terminal.

### OpenAI-compatible Ollama integration

The project uses the `openai` Python package, but points the client at an Ollama-compatible endpoint through `OLLAMA_BASE_URL`. This allows the code to use the familiar OpenAI chat-completions interface with a locally hosted or otherwise compatible model.

### Function/tool calling

The model receives descriptions of the available tools and can request them when appropriate:

- `get_current_time`
- `get_city_weather`
- `get_user_city`

The Python application executes the requested function and sends the result back to the model as a tool message.

### Multi-step agent execution

A single user request can result in several model/tool interactions. For example, a weather question about the user's location can require:

1. Calling `get_user_city`.
2. Calling `get_city_weather` with the returned city.
3. Generating a natural-language answer.

The number of model iterations for one request is limited to five by `MAX_STEPS`.

### Optional debug logging

Set `DEBUG=True` to display model tool requests, tool arguments, and tool results in colored debug output.

### Streaming example

`stream_test.py` provides a separate minimal example of streaming model output token-by-token instead of waiting for the complete response.

## Project structure

```text
.
├── README.md
├── simple_ai_assistant.py
├── tools.py
├── stream_test.py
├── LEARNINGS.md
├── .gitignore
└── utilities/
    └── utilities.py
```

### `simple_ai_assistant.py`

The main executable application. It:

1. Loads environment variables.
2. Creates an OpenAI-compatible client configured for Ollama.
3. Initializes the system prompt and conversation history.
4. Reads user input in a loop.
5. Sends the conversation and tool definitions to the model.
6. Executes any requested tools.
7. Sends tool results back to the model.
8. Prints the final answer.

### `tools.py`

Contains:

- The concrete tool implementations.
- The tool schemas exposed to the model.
- The mapping from model-requested tool names to Python functions.
- The generic tool-call dispatcher.

### `stream_test.py`

A standalone streaming-response example. It does not use the assistant's interactive loop or tools.

### `utilities/utilities.py`

Contains the shared `log()` helper used for optional debug output.

### `LEARNINGS.md`

Documents a prompt-design lesson: tools should extend the assistant's capabilities, not prevent it from answering questions that do not require tools.

## How the agent works

The main runtime flow is:

```text
User enters a message
        │
        ▼
Add message to conversation history
        │
        ▼
Send conversation and tool definitions to the model
        │
        ├── Model returns normal text
        │       └── Print final answer
        │
        └── Model requests one or more tools
                │
                ▼
        Parse tool arguments
                │
                ▼
        Execute Python function
                │
                ▼
        Add result to conversation history
                │
                ▼
        Ask model for the next response
```

The conversation history is stored in the `messages` list in memory. It includes:

- The initial system instruction.
- User messages.
- Assistant messages.
- Tool results.

The history is preserved while the process is running, so later questions can refer to earlier messages. It is not saved to disk and is lost when the program exits.

## Available tools

### `get_current_time`

Returns the current date and time from the machine running the assistant.

Example user request:

```text
What time is it?
```

The result is formatted as:

```text
YYYY-MM-DD HH:MM:SS
```

### `get_city_weather`

Retrieves current weather information from `wttr.in`.

Example user request:

```text
What is the weather in London?
```

The tool requests:

```text
https://wttr.in/London?format=3
```

The request has a ten-second timeout. A successful response returns the weather service's text. Non-success HTTP responses return a friendly failure message.

This tool requires network access.

### `get_user_city`

Returns the user's saved city. At present, the value is hard-coded:

```text
Dehradun
```

Example user requests:

```text
Where do I live?
What city am I from?
```

This is currently a simple placeholder for a future profile, database, or configuration-backed implementation.

## Requirements

You need:

- Python 3.
- An Ollama installation or another OpenAI-compatible chat-completions server.
- A chat model available through that server.
- Network access if you want to use the weather tool.

The Python dependencies used by the project are:

- `openai`
- `python-dotenv`
- `requests`

The repository currently does not include a `requirements.txt` or `pyproject.toml`, so these packages must be installed manually.

## Installation

### 1. Create a virtual environment

From the repository root:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install openai python-dotenv requests
```

### 3. Configure the environment

Create a `.env` file in the repository root:

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_MODEL=your-model-name
DEBUG=False
```

Replace `your-model-name` with a model available in your Ollama installation.

For a local Ollama server, the URL is commonly:

```text
http://localhost:11434/v1
```

The API key is accepted by the OpenAI client but is typically not used for local Ollama authentication. The value can still be set to a placeholder such as `ollama`.

## Running the assistant

Start the interactive assistant with:

```bash
python simple_ai_assistant.py
```

You should see a prompt similar to:

```text
PRIYANSHU-BAFILA:
```

Enter a question and press Enter. To stop the assistant, enter any of:

```text
exit
bye
quit
end
```

Example session:

```text
PRIYANSHU-BAFILA: What is Python?
Assistant: Python is a high-level programming language ...

PRIYANSHU-BAFILA: What city do I live in?
Assistant: Your saved city is Dehradun.

PRIYANSHU-BAFILA: exit
Assistant: See you later!
```

## Running the streaming example

To run the standalone streaming demonstration:

```bash
python stream_test.py
```

This sends the fixed prompt `Explain AI in 100 words` and prints each response fragment as it arrives.

Unlike the main assistant, this script:

- Does not prompt for user input.
- Does not maintain a conversation.
- Does not expose tools.
- Does not implement a multi-step agent loop.

## Configuration reference

| Variable | Required | Description |
|---|---:|---|
| `OLLAMA_BASE_URL` | Yes | Base URL for the OpenAI-compatible model API. |
| `OLLAMA_API_KEY` | Yes by client configuration | API key passed to the OpenAI client. Local Ollama commonly accepts a placeholder value. |
| `OLLAMA_MODEL` | Yes | Name of the model used for chat completions. |
| `DEBUG` | No | Enable debug logs only when set exactly to `True`. |

The `.env` file is ignored by Git through `.gitignore`, so local credentials and configuration are not intended to be committed.

## Error handling

Tool execution is wrapped by `run_tool()` in `tools.py`. This protects the main assistant from many tool-related failures, including:

- Invalid JSON arguments from the model.
- Missing or unexpected function arguments.
- Unknown tool names.
- Network failures from the weather request.
- Exceptions raised by tool functions.

Instead of terminating the process, the dispatcher returns an error string to the model as the tool result. The model can then explain the issue or provide an alternative response.

The main agent also has a step limit. If the model requests tools continuously for all five allowed steps, the assistant returns:

```text
Sorry, I couldn't provide a complete answer. Reached the maximum number of steps.
```

## Design choices

### General knowledge is not restricted by tools

The system prompt explicitly tells the model to answer general questions using its own knowledge. Tools are supplemental capabilities for information such as current weather or the machine's current time.

### Tool schemas are separate from implementation

The model sees the JSON-style definitions in `TOOLS`, while Python executes functions from `function_name_to_function_map`. This separation makes it possible to describe tools to the model without exposing implementation details.

### The model controls tool selection

The Python program provides the available tools but does not independently classify every user request. The model chooses whether to call a tool based on the tool descriptions and the conversation.

### The project uses an in-memory conversation

This keeps the example simple and avoids requiring a database or file format. It also means there is no persistence, user account system, or cross-session memory.

## Current limitations

The project is intentionally minimal and has several limitations:

- There is no dependency manifest.
- There are no automated tests.
- There is no explicit startup validation for missing environment variables.
- Conversation history is not persisted.
- `get_user_city()` always returns `Dehradun`.
- The main assistant does not stream its final response.
- Weather depends on the availability of the external `wttr.in` service.
- The application has no authentication or multi-user support.
- There is no structured logging system.
- There is no command-line configuration interface.
- Both executable scripts run their code at import time because they do not use an `if __name__ == "__main__":` guard.
- The number of tools and their mapping are maintained manually.

## Possible extensions

Natural next improvements include:

1. Add `requirements.txt` or `pyproject.toml`.
2. Add a `main()` function and `if __name__ == "__main__":` guards.
3. Validate required environment variables before creating the client.
4. Move the saved city into configuration or a user profile.
5. Add unit tests for tools and the dispatcher.
6. Add streaming output to the main assistant.
7. Add more tools, such as web search, reminders, or calculator operations.
8. Persist conversation history.
9. Add structured logging and clearer error types.
10. Add command-line arguments for model, endpoint, and debug mode.

## Troubleshooting

### The client cannot connect to Ollama

Check that:

- Ollama is running.
- `OLLAMA_BASE_URL` points to the correct endpoint.
- The configured model exists.
- The model name in `OLLAMA_MODEL` is spelled correctly.

### The model does not call tools

Tool calling depends on model support and model behavior. Check that:

- The model supports tool/function calling.
- The tool descriptions are being sent successfully.
- The request is specific enough to require live or user-specific information.
- `DEBUG=True` is set so you can inspect tool requests.

### Weather requests fail

Check that:

- The machine has internet access.
- `wttr.in` is reachable.
- The city name is valid.
- The request is not being blocked by a firewall or proxy.

### Python reports missing packages

Install the required dependencies inside the active virtual environment:

```bash
pip install openai python-dotenv requests
```

## Reading path

For a quick understanding of the project, read the files in this order:

1. `simple_ai_assistant.py` — the complete interactive agent loop.
2. `tools.py` — tool implementations, schemas, and dispatch.
3. `utilities/utilities.py` — debug logging.
4. `stream_test.py` — standalone streaming usage.
5. `LEARNINGS.md` — prompt-design rationale.

The most important control flow is in `simple_ai_assistant.py`, while the most important extension point is `tools.py`.

## License

No license file is currently included in the repository. Add an explicit license before distributing or reusing the project publicly.
