"""Part 4: read the documents, split them into chunks, embed each chunk, and save the index.

Run it once, and again whenever the files in content/ change:
    python part-4/ingest.py
"""

import json
import sys
from pathlib import Path

from openai import APIConnectionError, APIStatusError, OpenAI
from retrieve import INDEX_FILE, load_embedding_settings

CONTENT_DIR = Path(__file__).parent / "content"


def chunk_markdown(text: str, source: str) -> list[dict[str, str]]:
    """Split a markdown document into one chunk per '## ' section."""
    chunks: list[dict[str, str]] = []
    doc_title = ""
    heading = ""
    body: list[str] = []

    def flush() -> None:
        content = "\n".join(body).strip()
        if heading and content:
            chunks.append(
                {"source": source, "heading": heading, "text": f"{doc_title}: {heading}\n{content}"}
            )

    for line in text.splitlines():
        if line.startswith("# "):
            doc_title = line[2:].strip()
        elif line.startswith("## "):
            flush()
            heading = line[3:].strip()
            body = []
        else:
            body.append(line)
    flush()
    return chunks


def main() -> None:
    settings = load_embedding_settings()
    files = sorted(CONTENT_DIR.glob("*.md"))
    chunks: list[dict] = []
    for path in files:
        found = chunk_markdown(path.read_text(encoding="utf-8"), path.name)
        print(f"{path.name}: {len(found)} chunks")
        chunks.extend(found)
    if not chunks:
        sys.exit(f"No chunks found. Put markdown files with '## ' headings in {CONTENT_DIR}.")

    client = OpenAI(base_url=settings["LLM_BASE_URL"], api_key=settings["LLM_API_KEY"])
    try:
        response = client.embeddings.create(
            model=settings["EMBED_MODEL"], input=[chunk["text"] for chunk in chunks]
        )
    except (APIConnectionError, APIStatusError) as error:
        sys.exit(f"Could not embed the chunks: {type(error).__name__}. Check your .env settings.")
    for chunk, item in zip(chunks, response.data, strict=True):
        chunk["vector"] = item.embedding

    index = {"embed_model": settings["EMBED_MODEL"], "chunks": chunks}
    INDEX_FILE.write_text(json.dumps(index), encoding="utf-8")
    print(f"Processed {len(files)} files and {len(chunks)} chunks with {settings['EMBED_MODEL']}.")
    print(f"Embedding tokens used: {response.usage.total_tokens if response.usage else 'unknown'}.")
    print(f"Wrote {INDEX_FILE.name}.")


if __name__ == "__main__":
    main()
