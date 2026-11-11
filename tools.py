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
    }  
]

function_name_to_function_map={
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
}