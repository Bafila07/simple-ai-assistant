import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
)
EMBED_MODEL=os.getenv("EMBED_MODEL")

# get the embedding of the text using the EMBED_MODEL
def get_embeddings(text):
    response=client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


chunks={
    "c0": "Leave Policy - Maternity Leave\nMaternity leave is 26 weeks of paid leave for the first two children.",
    "c1": "Medical Policy - Maternity Cover\nHospitalization for childbirth is covered up to 75,000 rupees.",
    "c2": "Travel Expense - Reimbursement\nSubmit expense claims within 30 days of the trip. Approved claims are reimbursed within 7 working days.",
    "c3": "Tech Docs - Deployment Windows\nProduction deployments are allowed on Tuesdays and Thursdays between 11 AM and 4 PM."
}

ids=list(chunks.keys())
documents=list(chunks.values())

embeddings=[]
for s in documents:
    embedding=get_embeddings(s)
    embeddings.append(embedding)

    

chroma=chromadb.PersistentClient(path="./chroma_dbStorage")

company_knowledge_base=chroma.get_or_create_collection(
    name="company_knowledge_base",
    configuration={
        "space": "cosine", 
    }
)

company_knowledge_base.upsert( #it will update if an Id already exists, otherwise it will insert a new record
    ids=ids,
    documents=documents,
    embeddings=embeddings
)
company_knowledge_base.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings
)

query="What are the benefits of Maternity Leave?"
query_embedding=get_embeddings(query)

results=company_knowledge_base.query(
    query_embeddings=[query_embedding],
    n_results=1
)

print(results["documents"][0])



