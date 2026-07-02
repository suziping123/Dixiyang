import os
import chromadb

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data","mytest")
client=chromadb.PersistentClient(path=db_path)
collection = client.get_or_create_collection(name="mytest")
if __name__ == '__main__':
    print(collection.get())
    collection.delete(ids="doc1")
    print(collection.get())
    print(client.list_collections())
    collection = client.delete_collection(name="mytest")
    print(client.list_collections())
