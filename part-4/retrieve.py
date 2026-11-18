"""Part 4: find the chunks that are most related to a question.

Run it by itself to see what retrieval returns:
    python part-4/retrieve.py "What time do you close on Friday?"
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

INDEX_FILE = Path(__file__).parent / "index.json"

# How many chunks go into each request. Always this many, whatever the scores are.
TOP_K = 3

Chunk = dict[str, str | list[float]]


def load_embedding_settings() -> dict[str, str]:
    """Read the embedding settings from .env and stop early if one is missing."""
    load_dotenv()
    names = ("LLM_BASE_URL", "LLM_API_KEY", "EMBED_MODEL")
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        sys.exit(f"Missing settings in .env: {', '.join(missing)}")
    return {name: os.environ[name] for name in names}


def embed(client: OpenAI, model: str, texts: list[str]) -> list[list[float]]:
    """Turn each text into a vector. One API call for the whole list."""
    response = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]


def load_index(embed_model: str, path: Path = INDEX_FILE) -> list[Chunk]:
    """Load the saved chunks. Stop with a clear message if the index cannot be used."""
    if not path.exists():
        sys.exit("No index.json found. Run 'python part-4/ingest.py' first.")
    index = json.loads(path.read_text(encoding="utf-8"))
    if index["embed_model"] != embed_model:
        sys.exit(
            f"index.json was built with {index['embed_model']}, but EMBED_MODEL is "
            f"{embed_model}. Run 'python part-4/ingest.py' again."
        )
    return index["chunks"]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """How closely two vectors point the same way. Higher means more related."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def top_chunks(
    question_vector: list[float], chunks: list[Chunk], k: int = TOP_K
) -> list[tuple[float, Chunk]]:
    """Score every chunk against the question and return the best k."""
    query = np.array(question_vector)
    scored = [(cosine_similarity(query, np.array(chunk["vector"])), chunk) for chunk in chunks]
    return sorted(scored, key=lambda pair: pair[0], reverse=True)[:k]


def retrieve(
    client: OpenAI, embed_model: str, chunks: list[Chunk], question: str, k: int = TOP_K
) -> list[tuple[float, Chunk]]:
    """Embed the question and return the k most related chunks with their scores."""
    question_vector = embed(client, embed_model, [question])[0]
    return top_chunks(question_vector, chunks, k)


def chunk_label(chunk: Chunk) -> str:
    return f"{chunk['source']} / {chunk['heading']}"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit('Usage: python part-4/retrieve.py "your question"')
    question = sys.argv[1]
    settings = load_embedding_settings()
    chunks = load_index(settings["EMBED_MODEL"])
    client = OpenAI(base_url=settings["LLM_BASE_URL"], api_key=settings["LLM_API_KEY"])
    try:
        results = retrieve(client, settings["EMBED_MODEL"], chunks, question)
    except (APIConnectionError, APIStatusError) as error:
        sys.exit(f"Could not embed the question: {type(error).__name__}.")
    print(f"Question: {question}\n")
    for rank, (score, chunk) in enumerate(results, start=1):
        print(f"{rank}. score {score:.3f}  [{chunk_label(chunk)}]")
        print(f"{chunk['text']}\n")


if __name__ == "__main__":
    main()
