import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
)
EMBED_MODEL=os.getenv("EMBED_MODEL")
KB_FOLDER=os.getenv("KB_FOLDER")




# Get Embeddings from the model
def get_embeddings(text):
    response=client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding




# Get cosine similarity between two vectors
def cosine_similarity(A,B):
    dot_product=np.dot(A,B)
    norm_A=np.linalg.norm(A)
    norm_B=np.linalg.norm(B)
    return dot_product/(norm_A*norm_B)




# load the documents
def load_documents(folder=KB_FOLDER):
    documents=[]
    for filename in os.listdir(folder):
        if not filename .endswith(".txt"):
            continue
        path=os.path.join(folder,filename)
        with open(path,"r",encoding="UTF-8") as f:
            documents.append(
                {
                "source":filename,
                "text":f.read()
                }
            )
    return documents




# Add Embeddings in the document
def add_embeddings(documents):
    for document in documents:
        vector=get_embeddings(document["text"])
        document["embedding"]=vector
    return documents



def search_documents(query,documents,top_k=3):
    query_vector=get_embeddings(query)
    result=[]
    for document in documents:
        score=cosine_similarity(query_vector,document["embedding"])
        result.append(
            {
                "source":document["source"],
                "text":document["text"],
                "size":len(document["text"]),
                "score":score
            }
        )
    result.sort(key=lambda x:x["score"],reverse=True)
    return result[:top_k]

# testing method
def test_search(user_query,document,top_k=3):
    print(f"User Query: {user_query}\n")
    results=search_documents(user_query,document,top_k)
    for r in results:
        print(f"Source: {r['source']} - Score: {r['score']:.4f} - Size: {r['size']}\n")

# Let's test the search function
documents=load_documents()
documents=add_embeddings(documents)

print(f"Documents loaded and embeddings added. Total documents: {len(documents)}\n")
user_query="How many days off will i get for maternity leave?"
test_search(user_query,documents,top_k=3)