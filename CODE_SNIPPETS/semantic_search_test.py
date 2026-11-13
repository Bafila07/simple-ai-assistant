# Standard libraries
import os
import numpy as np

# Third-party libraries
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
)

def get_embedding(text):
    response = client.embeddings.create(
        model=os.getenv("EMBED_MODEL"),
        input=text,
    )
    return response.data[0].embedding

def cosine_similarity(A,B):
    dot_product = np.dot(A,B)
    norm_A = np.linalg.norm(A)
    norm_B = np.linalg.norm(B)
    return dot_product / (norm_A * norm_B)  



text1="Python is a popular programming language"
text2="Python is widely used in the field of artificial intelligence and machine learning"
text3="I love apples and oranges"

embedding1 = get_embedding(text1)
embedding2 = get_embedding(text2)
embedding3 = get_embedding(text3)
similarity1 = cosine_similarity(embedding1, embedding2)
similarity2 = cosine_similarity(embedding1, embedding3)
similarity3 = cosine_similarity(embedding2, embedding3)


print(f"Similarity between text1 and text2: {similarity1:.4f}")
print(f"Similarity between text1 and text3: {similarity2:.4f}")
print(f"Similarity between text2 and text3: {similarity3:.4f}")

text4="Artifical intellgeince and machine learning are mainly implemened using python programming language"
embedding4 = get_embedding(text4)
similarity4 = cosine_similarity(embedding2, embedding4)
print(f"Similarity between text2 and text4: {similarity4:.4f}")


text5="apples and ladyfingers are loved by me."
embedding5 = get_embedding(text5)
text6="I love apples and ladyfinger"
embedding6 = get_embedding(text6)
similarity5 = cosine_similarity(embedding5, embedding6)
print(f"Similarity between text5 and text6: {similarity5:.4f}")