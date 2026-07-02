import os
import chromadb

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data", "mytest")
client = chromadb.PersistentClient(path=db_path)
collection = client.get_or_create_collection(name="mytest")

print(collection.count())
print(collection.get())
print(collection.query(query_embeddings=[1,2,3]))