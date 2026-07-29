# samples/test_rag.py
import chromadb
import ollama


client = chromadb.PersistentClient(path="./data/test_db")
collection = client.get_or_create_collection(name="test_collection")


chunks = [
    "The mitochondria is the powerhouse of the cell and generates ATP.",
    "Photosynthesis is the process used by plants to convert light into energy.",
    "The structural framework of a building is called its skeleton."
]


print("Encoding and saving sentences...")
for i, text in enumerate(chunks):
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    collection.upsert(
        ids=[f"id_{i}"],
        embeddings=[response["embedding"]],
        documents=[text]
    )


question = "How do plants make energy?"
print(f"\nSearching for: '{question}'")

query_response = ollama.embeddings(model="nomic-embed-text", prompt=question)
results = collection.query(
    query_embeddings=[query_response["embedding"]],
    n_results=1
)

print("\n--- Closest Match Found in Database ---")
print(results['documents'][0][0])
