import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

DATA_DIR = "./data"
STORAGE_DIR = "./storage"


def ingest_docs(doc_dir=DATA_DIR, persist_dir=STORAGE_DIR):
    if not os.path.exists(doc_dir):
        raise FileNotFoundError(f"Documents directory '{doc_dir}' not found.")
    documents = SimpleDirectoryReader(doc_dir).load_data()

    # Use local HF embeddings to avoid API keys on ingest
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir)
    print(f"Indexed {len(documents)} documents and saved index to '{persist_dir}'.")


if __name__ == "__main__":
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    ingest_docs()
