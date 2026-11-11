import requests
from datetime import datetime
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url=f"https://wttr.in/{city}?format=3"
    response=requests.get(url,timeout=10)
    if response.status_code==200:
        return response.text
    else:
        return f"Could not retrieve weather for {city}. Please try again later."

def get_user_city():
    return "Dehradun"

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
                        "description": "The name of the city to get the weather for."
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
            "description": "Returns the user's saved city. Call this tool when the user asks questions such as “Where do I live?” or “What city am I from?” Do not use it for weather or other location-related requests.",
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
    "get_city_weather": get_city_weather,
    "get_user_city": get_user_city

}