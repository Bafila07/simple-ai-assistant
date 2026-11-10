
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),  
)
messages=[]
while True:
    user_input=input("PRIYANSHU-BAFILA: ")
    if user_input.lower() in ["exit","bye","quit","end"]:
        print("Assistant: See you later!")
        break
    messages.append(
        {
            "role":"system",
            "content":"You are an expert teacher and interview mentor. Explain each concept clearly and simply for placement preparation. Include the core idea, a relatable analogy, and one practical real-world example. Keep the response concise and under 100 words."
        }
    )
    messages.append(
        {
            "role":"user",
            "content": user_input
        }
    )
    response=client.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL"),
        messages=messages
    )
    messages.append(
        {
            "role":"assistant",
            "content": response.choices[0].message.content
        }
    )
    print("Assistant: " + response.choices[0].message.content)