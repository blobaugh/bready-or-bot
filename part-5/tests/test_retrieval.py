"""Tests for chunking, ranking, and message assembly. Fake vectors only: no network, no key."""

import chat
import pytest
import retrieve
from ingest import chunk_markdown

DOC = """# Shop Policies

> A note that comes before any section.

Some text before the first section.

## Opening hours
- Friday: 6:30 am to 7:00 pm

## Delivery
We do not deliver.

## Empty section

## Last section
The final words.
"""


def test_one_chunk_per_section_and_the_empty_one_is_skipped():
    chunks = chunk_markdown(DOC, "policies.md")
    assert [c["heading"] for c in chunks] == ["Opening hours", "Delivery", "Last section"]


def test_the_document_title_is_in_the_chunk_text():
    chunk = chunk_markdown(DOC, "policies.md")[0]
    assert chunk["text"] == "Shop Policies: Opening hours\n- Friday: 6:30 am to 7:00 pm"
    assert chunk["source"] == "policies.md"


def test_text_before_the_first_section_is_skipped():
    text = " ".join(c["text"] for c in chunk_markdown(DOC, "policies.md"))
    assert "comes before any section" not in text
    assert "before the first section" not in text


def test_a_document_with_no_sections_gives_no_chunks():
    assert chunk_markdown("# Title\nJust text.", "x.md") == []


CHUNKS = [
    {"source": "a.md", "heading": "East", "text": "east", "vector": [1.0, 0.0]},
    {"source": "b.md", "heading": "North", "text": "north", "vector": [0.0, 1.0]},
    {"source": "c.md", "heading": "Northeast", "text": "both", "vector": [1.0, 1.0]},
]


def test_chunks_are_ranked_by_similarity_best_first():
    scored = retrieve.top_chunks([0.9, 0.1], CHUNKS, k=3)
    assert [chunk["heading"] for _, chunk in scored] == ["East", "Northeast", "North"]
    assert scored[0][0] > scored[1][0] > scored[2][0]


def test_only_k_chunks_are_returned():
    assert len(retrieve.top_chunks([0.0, 1.0], CHUNKS, k=2)) == 2


def test_length_does_not_change_the_score():
    short = retrieve.top_chunks([1.0, 0.0], CHUNKS, k=1)[0][0]
    long = retrieve.top_chunks([50.0, 0.0], CHUNKS, k=1)[0][0]
    assert short == pytest.approx(long) == pytest.approx(1.0)


def test_the_user_message_has_the_context_and_the_question():
    scored = retrieve.top_chunks([1.0, 0.0], CHUNKS, k=2)
    message = chat.build_user_message("Which way is east?", scored, guardrails=False)
    assert "[a.md / East]" in message
    assert "Customer question: Which way is east?" in message


def test_the_system_message_is_still_first_with_retrieval(monkeypatch):
    sent = []

    def fake_stream(client, model, messages, temperature, max_tokens=None):
        sent.append(messages)
        return "ok", 1, 1

    monkeypatch.setattr(chat, "stream_reply", fake_stream)
    monkeypatch.setattr(
        chat, "retrieve", lambda client, model, chunks, question: [(0.9, CHUNKS[0])]
    )
    system = {"role": "system", "content": "You are Crumb."}
    history: list[chat.Message] = []
    chat.take_turn(
        None, "model", system, 0.3, history, "Which way is east?", "embed", CHUNKS, guardrails=False
    )
    assert sent[0][0] == system
    assert "[a.md / East]" in sent[0][-1]["content"]
    assert "Which way is east?" in sent[0][-1]["content"]
    # The history keeps the plain question, not the question with the passages.
    assert history[0] == {"role": "user", "content": "Which way is east?"}


def test_a_missing_index_stops_with_a_message(tmp_path):
    with pytest.raises(SystemExit, match="ingest.py"):
        retrieve.load_index("embed-a", tmp_path / "index.json")


def test_an_index_from_another_embedding_model_stops_with_a_message(tmp_path):
    path = tmp_path / "index.json"
    path.write_text('{"embed_model": "embed-a", "chunks": []}', encoding="utf-8")
    with pytest.raises(SystemExit, match="ingest.py"):
        retrieve.load_index("embed-b", path)
    assert retrieve.load_index("embed-a", path) == []
