import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
)

stream = client.chat.completions.create(
    model=os.getenv("OLLAMA_MODEL"),
    messages=[
        {
            "role": "user",
            "content": "Explain AI in 100 words",
        }
    ],
    stream=True,
)



assigned = False
full_response=""
for chunk in stream:
    piece = chunk.choices[0].delta.content
    if piece and assigned == False:
        print("Assistant:    ", end="", flush=True)
        assigned = True
    if piece:
        print(piece, end="", flush=True)
        full_response += piece
        