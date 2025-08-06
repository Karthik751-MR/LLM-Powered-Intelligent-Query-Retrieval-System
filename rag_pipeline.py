# In rag_pipeline.py

import logging
from llama_index.core import Settings, VectorStoreIndex
from llm_config import get_llm_and_embed, LLM_PRIORITY, LOCAL_LLM_MODELS


async def query_and_get_answer(index: VectorStoreIndex, question: str) -> dict:
    """
    Queries the index using the LLM fallback logic, including the nested
    loop for local models, and returns the answer.
    """
    last_exception = None
    for provider_name in LLM_PRIORITY:
        try:
            logging.info(
                f"--- Attempting query with provider type: {provider_name} ---"
            )

            # --- FIX STARTS HERE: Re-introducing the local model loop ---
            if provider_name == "local":
                for local_model_name in LOCAL_LLM_MODELS:
                    try:
                        # Pass the specific local model name
                        llm, embed_model = get_llm_and_embed(
                            provider_name, local_model_name=local_model_name
                        )
                        Settings.llm = llm
                        Settings.embed_model = embed_model

                        query_engine = index.as_query_engine(similarity_top_k=5)
                        ans = await query_engine.aquery(question)

                        logging.info(
                            f"Successfully got answer from local model '{local_model_name}'."
                        )
                        return {"answer": ans.response}
                    except Exception as e:
                        logging.warning(
                            f"--- Failed on local model {local_model_name}: {e} ---"
                        )
                        last_exception = e
                # If all local models failed, continue to the next main provider (if any)
                continue
            # --- FIX ENDS HERE ---

            # This part handles non-'local' providers like Gemini
            else:
                llm, embed_model = get_llm_and_embed(provider_name)
                Settings.llm = llm
                Settings.embed_model = embed_model

                query_engine = index.as_query_engine(similarity_top_k=5)
                ans = await query_engine.aquery(question)

                logging.info(
                    f"Successfully got answer from provider '{provider_name}'."
                )
                return {"answer": ans.response}

        except Exception as e:
            logging.error(f"--- Failed on provider {provider_name}: {e} ---")
            last_exception = e

    # If all providers failed
    logging.critical(f"All LLM providers failed. Last error: {last_exception}")
    raise Exception(f"All LLM providers failed. Last error: {last_exception}")
