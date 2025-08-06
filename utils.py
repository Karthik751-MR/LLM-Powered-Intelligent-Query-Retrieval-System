import os
import aiohttp
import asyncio
import tempfile
import httpx
import logging
from pathlib import Path
from urllib.parse import urlparse
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


async def download_file(
    client: httpx.AsyncClient, url: str, temp_path: Path, file_number: int
):
    """Helper function to download a single file, preserving its extension."""
    try:
        # --- MODIFICATION START ---
        # Try to get the original filename from the URL path
        parsed_url = urlparse(url)
        original_filename = Path(parsed_url.path).name
        # Fallback to a generic name if the URL path is unusual
        if not original_filename or "." not in original_filename:
            original_filename = (
                f"doc_{file_number}.pdf"  # Default to pdf if undetectable
            )

        file_path = temp_path / original_filename
        # --- MODIFICATION END ---

        logging.info(f"Downloading {url} to {file_path}")
        response = await client.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)

    except httpx.RequestError as e:
        logging.error(f"Error downloading {url}: {e}")
        raise


async def build_index_from_urls(urls: list[str]) -> VectorStoreIndex:
    """
    Asynchronously downloads files from URLs, saves them to a temporary
    directory with correct extensions, and builds an index.
    """
    async with httpx.AsyncClient() as client:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Pass the file number to the download helper for fallback naming
            download_tasks = [
                download_file(client, url, temp_path, i + 1)
                for i, url in enumerate(urls)
            ]

            await asyncio.gather(*download_tasks)
            logging.info(f"Successfully downloaded {len(urls)} files.")

            # No change needed here! SimpleDirectoryReader handles the rest.
            reader = SimpleDirectoryReader(input_dir=temp_dir)
            documents = reader.load_data()
            logging.info(
                f"Loaded {len(documents)} documents of various types for indexing."
            )

            logging.info("Setting embedding model to bge-base-en-v1.5")
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-base-en-v1.5"
            )

            index = VectorStoreIndex.from_documents(documents)
            logging.info("Successfully created in-memory vector index.")
            return index
