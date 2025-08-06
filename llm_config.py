import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Load Model Configuration ---
LLM_PRIORITY = os.getenv("LLM_PRIORITY", "gemini,local").split(",")
# We now load a list of local models
LOCAL_LLM_MODELS = os.getenv("LOCAL_LLM_MODELS", "llama3").split(",")

# Load API Keys
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")


def get_llm_and_embed(llm_name, local_model_name=None):
    """
    Returns the LLM and Embedding model based on the provider name.
    """
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    # --- Provider 1: Google Gemini ---
    if llm_name == "gemini":
        from llama_index.llms.gemini import Gemini

        print("--- Using provider: Google Gemini ---")
        llm = Gemini(
            model_name="models/gemini-1.5-flash", api_key=GOOGLE_GEMINI_API_KEY
        )
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        return (llm, embed_model)

    # --- Provider 2: Local Models via Ollama ---
    elif llm_name == "local":
        from llama_index.llms.ollama import Ollama

        # Use the specific local model passed to the function
        print(f"--- Using local provider: Ollama ({local_model_name}) ---")
        llm = Ollama(model=local_model_name, request_timeout=120.0)
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        return (llm, embed_model)

    else:
        raise ValueError(f"Unknown LLM backend: {llm_name}")
