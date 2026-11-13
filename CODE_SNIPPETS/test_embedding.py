# Standard libraries
import os

# Third-party libraries
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
)

response = client.embeddings.create(
    model=os.getenv("EMBED_MODEL"),
    input=[
        "Hello, world!",
        "This is a test of the embedding API.",
    ],
)
for i, embedding in enumerate(response.data):
    print(f"Embedding for input {i}: {embedding.embedding[:5]}...")  # Print first 5 dimensions