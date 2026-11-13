import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
)
EMBED_MODEL=os.getenv("EMBED_MODEL")
KB_FOLDER=os.getenv("KB_FOLDER")
VECTOR_STORE_FILE=os.getenv("VECTOR_STORE_FILE")

def get_embeddings(text):
    response=client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(A, B):
    norm_A = np.linalg.norm(A)
    norm_B = np.linalg.norm(B)

    if norm_A == 0 or norm_B == 0:
        return 0.0

    return np.dot(A, B) / (norm_A * norm_B)


#load the documents
def load_documents(folder=KB_FOLDER):
    documents=[]
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
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


def add_embeddings(chunks):
    for chunk in chunks:
        vector=get_embeddings(chunk["text"])
        chunk["embedding"]=vector
    return chunks


# Search the chunks for the query and return the top_k results
def search(query,chunks,top_k=3):
    query_vector=get_embeddings(query)
    result=[]
    for chunk in chunks:
        score=cosine_similarity(query_vector,chunk["embedding"])
        result.append(
            {
                "chunk_id":chunk["chunk_id"],
                "source":chunk["source"],
                "text":chunk["text"],
                "size":len(chunk["text"]),
                "score":score
            }
        )
    result.sort(key=lambda x:x["score"],reverse=True)
    return result[:top_k]

# Test the search function
def test(user_query,chunks,top_k=3):
    print(f"User Query: {user_query}\n")
    results=search(user_query,chunks,top_k)
    for r in results:
        print(f"Source: {r['source']} - Score: {r['score']:.4f} - Size: {r['size']}\n")
        print(f"Text: {r['text']}\n")


# Take one document at a time and split it into chunks based on paragraphs (double newlines)
def chunk_document(document):
    chunks=[]
    chunk_id=0
    for part in document["text"].split("\n\n"):
        part=part.strip()
        if not part:
            continue
        chunks.append(
            {
                "chunk_id":f"{document['source']}_chunk_{chunk_id}",
                "source":document["source"],
                "text":part
            }
        )
        chunk_id+=1
    return chunks

# Take all documents and split them into chunks
def create_chunks():
    documents=load_documents()
    chunks=[]
    for document in documents:
        chunks.extend(chunk_document(document))
    return chunks

def save_vector_store(chunks):
    with open(VECTOR_STORE_FILE,"w",encoding="UTF-8") as f:
        json.dump(chunks,f,ensure_ascii=False,indent=4)

def load_vector_store():
    with open(VECTOR_STORE_FILE,"r",encoding="UTF-8") as f:
        return json.load(f)
chunks = []

if os.path.exists(VECTOR_STORE_FILE):
    chunks = load_vector_store()
    print(
        f"Loaded {len(chunks)} chunks from "
        f"{VECTOR_STORE_FILE}"
    )
else:
    chunks = create_chunks()
    chunks = add_embeddings(chunks)
    save_vector_store(chunks)

    print(
        f"Created {len(chunks)} chunks and saved to "
        f"{VECTOR_STORE_FILE}"
    )
 
print(f"Total chunks available: {len(chunks)}\n")
user_query="What are the benefits of Maternity Leave?"

test(user_query,chunks,top_k=3)