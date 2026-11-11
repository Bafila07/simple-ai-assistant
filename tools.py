from datetime import datetime
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Tool definition given to the AI
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
    }
]

function_name_to_function_map={
    "get_current_time": get_current_time,
}