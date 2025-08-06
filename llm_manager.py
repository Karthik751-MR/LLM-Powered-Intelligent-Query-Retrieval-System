import os
from dotenv import load_dotenv

load_dotenv()

llm_priority = os.getenv("LLM_PRIORITY", "openai,local").split(",")
local_llm_model = os.getenv("LOCAL_LLM_MODEL", "llama3")

# Import LLM clients
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI, OpenAIEmbedding

# Assume you have similar imports for Anthropic, Gemini, and your local LLM:
# from llama_index.llms.anthropic import Anthropic, AnthropicEmbedding
# from llama_index.llms.gemini import Gemini, GeminiEmbedding
# from llama_index.llms.ollama import Ollama


def get_llm_and_embedding(llm_name):
    if llm_name == "openai":
        return (
            OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
            OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY")),
        )
    elif llm_name == "claude":
        from llama_index.llms.anthropic import Anthropic, AnthropicEmbedding

        return (
            Anthropic(model="claude-3-opus", api_key=os.getenv("ANTHROPIC_API_KEY")),
            AnthropicEmbedding(api_key=os.getenv("ANTHROPIC_API_KEY")),
        )
    elif llm_name == "gemini":
        from llama_index.llms.gemini import Gemini, GeminiEmbedding

        return (
            Gemini(
                model_name="models/gemini-2.5-flash-lite",
                api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
            ),
            GeminiEmbedding(api_key=os.getenv("GOOGLE_GEMINI_API_KEY")),
        )
    elif llm_name == "local":
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        return (
            Ollama(model=local_llm_model),
            HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5"),
        )
    else:
        raise ValueError(f"Unknown LLM backend: {llm_name}")


def try_llm_fallbacks(prompt):
    last_exception = None
    for llm_name in llm_priority:
        try:
            llm, embed = get_llm_and_embedding(llm_name)
            Settings.llm = llm
            Settings.embed_model = embed
            # Make your call to LLM here with the prompt or query...
            # For demonstration:
            print(f"Trying {llm_name}...")
            response = llm.complete(prompt)  # Adapt according to LLM API
            return response
        except Exception as e:
            print(f"Error with {llm_name}: {e}. Trying next LLM in priority.")
            last_exception = e
            continue
    raise Exception(f"All LLMs failed. Last exception: {last_exception}")
