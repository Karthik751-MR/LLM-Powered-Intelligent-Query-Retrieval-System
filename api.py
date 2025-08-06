import logging
import asyncio
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import build_index_from_urls
from rag_pipeline import query_and_get_answer

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="HackRx Insurance RAG LLM API")


class RunRequest(BaseModel):
    documents: List[str]
    questions: List[str]


class RunResponse(BaseModel):
    answers: List[Dict]


@app.post("/hackrx/run", response_model=RunResponse)
async def hackrx_run(payload: RunRequest):
    try:
        index = await build_index_from_urls(payload.documents)
        # Run all questions at once—super fast!
        tasks = [query_and_get_answer(index, q) for q in payload.questions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        final_answers = [
            (
                res
                if not isinstance(res, Exception)
                else {"answer": "Failed to get answer. All LLM providers failed."}
            )
            for res in results
        ]
        return RunResponse(answers=final_answers)
    except Exception as e:
        logging.critical(f"A critical error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
