import faiss
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384
index = faiss.IndexFlatL2(dimension)
documents = []

def reset_store():
    global index, documents
    index = faiss.IndexFlatL2(dimension)
    documents = []

def add_documents(chunks):
    global documents
    embeddings = embedder.encode(chunks)
    index.add(embeddings)
    documents.extend(chunks)

def get_context(query, top_k=5):
    q_embed = embedder.encode([query])
    D, I = index.search(q_embed, top_k)
    results = [documents[i] for i in I[0]]
    return "\n".join(results)

