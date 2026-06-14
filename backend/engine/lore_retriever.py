"""ChromaDB lore retrieval with local sentence-transformers embeddings."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.utils import embedding_functions

from utils.logger import get_logger
from utils.paths import resolve_data_path

logger = get_logger(__name__)

COLLECTION_NAME = "eldervale_lore"
DEFAULT_LORE_DIR = str(resolve_data_path("LORE_DIR", "data/lore"))
DEFAULT_CHROMA_DIR = str(resolve_data_path("CHROMA_PERSIST_DIR", "data/chroma"))


def _get_client(persist_dir: str | None = None) -> chromadb.PersistentClient:
    path = persist_dir or DEFAULT_CHROMA_DIR
    Path(path).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=path)


def _get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def _parse_markdown_chunks(content: str, source_file: str) -> List[dict]:
    """Split markdown at ## headings into chunks."""
    chunks = []
    parts = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    for i, part in enumerate(parts):
        part = part.strip()
        if not part or len(part) < 20:
            continue
        title_match = re.search(r"^#+ (.+)$", part, re.MULTILINE)
        title = title_match.group(1) if title_match else f"chunk_{i}"
        chunk_id = f"{source_file}::{title.replace(' ', '_').lower()}::{i}"
        tags_match = re.search(r"\*\*Tags:\*\*\s*(.+)$", part, re.MULTILINE)
        tags = tags_match.group(1).strip() if tags_match else ""
        chunks.append(
            {
                "id": chunk_id,
                "document": part,
                "metadata": {"source": source_file, "title": title, "tags": tags},
            }
        )
    return chunks


def index_lore(
    lore_dir: str | None = None,
    persist_dir: str | None = None,
    force: bool = False,
) -> int:
    """Index all markdown lore files into ChromaDB. Returns chunk count."""
    lore_path = Path(lore_dir or DEFAULT_LORE_DIR)
    client = _get_client(persist_dir)
    ef = _get_embedding_function()

    if force:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    try:
        collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
        if not force and collection.count() > 0:
            logger.info("Lore collection already indexed with %d chunks", collection.count())
            return collection.count()
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=ef
    )

    all_chunks: List[dict] = []
    for md_file in sorted(lore_path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        if md_file.name == "session_notes.md" and len(content.strip()) < 50:
            continue
        all_chunks.extend(_parse_markdown_chunks(content, md_file.name))

    if not all_chunks:
        logger.warning("No lore chunks found in %s", lore_path)
        return 0

    # Clear and re-upsert
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["document"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )

    logger.info("Indexed %d lore chunks from %s", len(all_chunks), lore_path)
    return len(all_chunks)


def get_collection_count(persist_dir: str | None = None) -> int:
    try:
        client = _get_client(persist_dir)
        ef = _get_embedding_function()
        collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
        return collection.count()
    except Exception:
        return 0


def query_lore(
    query: str,
    n_results: int = 4,
    persist_dir: str | None = None,
) -> List[dict]:
    """Query lore knowledge base. Returns list of {id, document, metadata, distance}."""
    try:
        client = _get_client(persist_dir)
        ef = _get_embedding_function()
        collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
        results = collection.query(query_texts=[query], n_results=n_results)
        output = []
        if results and results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                output.append(
                    {
                        "id": chunk_id,
                        "document": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                    }
                )
        return output
    except Exception as e:
        logger.warning("Lore retrieval failed, GM will use fallback: %s", e)
        return []
