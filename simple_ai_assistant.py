
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),  
)
while True:
    user_input=input("PRIYANSHU-BAFILA: ")
    if user_input.lower() in ["exit","bye","quit","end"]:
        print("Assistant: See you later!")
        break
    response=client.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL"),
        messages=[
            { 
                "role": "user", 
                "content": user_input
            }
        ]
    )
    print("Assistant: " + response.choices[0].message.content)