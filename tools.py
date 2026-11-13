# Standard library imports
import json
from datetime import datetime

# Third-party imports
import requests

# Local imports
from utilities.utilities import log
from rag import search


# Returns the current date and time
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Returns the current weather for a given city
def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"

    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        return response.text
    else:
        return (
            f"Could not retrieve weather for {city}. "
            "Please try again later."
        )


# Returns the user's saved city
def get_user_city():
    return "Dehradun"


# 
def search_knowledge_base(query):

    results = search(query, top_k=2)

    log(f"📚 Knowledge base search: {query}")
    for r in results:
        log(f"   {r['score']:.2f} - {r['source']} #{r['chunk_id']}")

    blocks = []
    for r in results:
        sourceFileName = r['source']
        chunkId        = r['chunk_id']
        chunkText      = r['text']

        header = f"[{sourceFileName} #{chunkId}]"
        block  = f"{header}\n{chunkText}"
        blocks.append(block)

    return "\n\n".join(blocks)


# Executes the tool requested by the LLM
def run_tool(tool_call):

    # Get the name of the tool requested by the model
    tool_name = tool_call.function.name

    tool_args = {}

    try:

        # Convert the tool arguments from JSON to a Python dictionary
        tool_args = json.loads(
            tool_call.function.arguments or "{}"
        )

        log(
            f" 🔧 Tool call: {tool_name} "
            f"with arguments: {tool_args}"
        )

        # Find the Python function for the requested tool
        tool_function = function_name_to_function_map.get(
            tool_name
        )

        # Run the tool with the given arguments
        result = tool_function(**tool_args)

    except Exception as e:

        # Return an error instead of crashing the agent
        result = f"Error executing tool {tool_name}: {str(e)}"

    # Log the result returned by the tool
    log(f"   └─ 📋 Result: {result}")

    return result


# Tool definitions given to the AI
TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "Returns the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": (
                            "The name of the city to get "
                            "the weather for."
                        )
                    }
                },
                "required": ["city"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_user_city",
            "description": (
                "Returns the user's saved city. "
                "Call this tool when the user asks questions "
                "such as 'Where do I live?' or "
                "'What city am I from?'. "
                "Do not use it for weather or other "
                "location-related requests."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description" : "Searches the Zorvex Technologies company knowledge base: leave, medical, HR, hiring, tech, incident "
                            "reports and travel expense policies. Use it for any question about company policies or documents. "
                            "Returns the most relevant passages with their source.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question, rewritten as a short, self-contained search query.",
                    }
                },
                "required": ["query"],
            },
        },
    }
]


# Maps each tool name to its actual Python function
function_name_to_function_map = {

    "get_current_time": get_current_time,

    "get_city_weather": get_city_weather,

    "get_user_city": get_user_city,

    "search_knowledge_base": search_knowledge_base

}