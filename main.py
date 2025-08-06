import os
import asyncio
from llama_index.core import Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import load_index_from_storage

# We will import the model lists here
from llm_config import get_llm_and_embed, LLM_PRIORITY, LOCAL_LLM_MODELS
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

STORAGE_DIR = "./storage"

def load_index():
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
    index = load_index_from_storage(storage_context)
    return index

async def query_index_async(index, user_query):
    last_exception = None

    # Loop through the main priority list (e.g., "gemini", "local")
    for provider_name in LLM_PRIORITY:
        try:
            print(f"\n--- Attempting query with provider type: {provider_name} ---")

            # If the provider is 'local', we loop through the local models
            if provider_name == "local":
                for local_model in LOCAL_LLM_MODELS:
                    try:
                        llm, embed_model = get_llm_and_embed(provider_name, local_model_name=local_model)
                        Settings.llm = llm
                        Settings.embed_model = embed_model

                        query_engine = index.as_query_engine(similarity_top_k=5)
                        response = await query_engine.aquery(user_query)

                        print(f"\n>>> Answer from {local_model} model:\n{response.response}\n")
                        return response # Success, exit the function
                    except Exception as e:
                        print(f"--- Failed on local model {local_model} due to error: {e} ---")
                        last_exception = e
                # If all local models failed, continue to the next main provider (if any)
                continue

            # This part handles non-'local' providers like Gemini
            else:
                llm, embed_model = get_llm_and_embed(provider_name)
                Settings.llm = llm
                Settings.embed_model = embed_model

                query_engine = index.as_query_engine(similarity_top_k=5)
                response = await query_engine.aquery(user_query)

                print(f"\n>>> Answer from {provider_name} model:\n{response.response}\n")
                return response # Success, exit the function

        except Exception as e:
            print(f"--- Failed on provider {provider_name} due to error: {e} ---")
            last_exception = e

    # If all providers and all local models have failed
    raise Exception(f"All LLM backends failed. Last error: {last_exception}")


# Main execution block
if __name__ == "__main__":
    print("--- Setting up global embedding model ---")
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

    print("--- Loading index from storage ---")
    index = load_index()

    test_query = "Personal Accident Covers, Percentage of Sum Insured Payable as Compensation"

    print(f"\n--- Starting query for: '{test_query}' ---")
    asyncio.run(query_index_async(index, test_query))
