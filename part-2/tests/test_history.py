"""Tests for the history helpers. No network and no API key needed."""

import chat
import pytest
from openai import APIConnectionError


def make_history(pairs: int) -> list[chat.Message]:
    """Build saved history: whole question and answer pairs, starting with the user."""
    history: list[chat.Message] = []
    for i in range(pairs):
        history.append({"role": "user", "content": f"question {i}"})
        history.append({"role": "assistant", "content": f"answer {i}"})
    return history


def test_trim_keeps_only_the_last_messages():
    history = make_history(5)
    assert chat.trim_history(history, 4) == history[-4:]


def test_trim_returns_everything_when_the_history_is_short():
    history = make_history(2)
    assert chat.trim_history(history, 20) == history


def test_trimmed_history_starts_with_a_user_message():
    assert chat.MAX_HISTORY_MESSAGES % 2 == 0
    history = make_history(chat.MAX_HISTORY_MESSAGES)
    trimmed = chat.trim_history(history)
    assert len(trimmed) == chat.MAX_HISTORY_MESSAGES
    assert trimmed[0]["role"] == "user"


def test_successful_turn_remembers_the_question_then_the_reply(monkeypatch):
    sent = []

    def fake_stream(client, model, messages):
        sent.append(messages)
        return "Hi Sam", 7, 2

    monkeypatch.setattr(chat, "stream_reply", fake_stream)
    history: list[chat.Message] = []
    tokens = chat.take_turn(None, "model", history, "My name is Sam.")
    assert tokens == (7, 2)
    assert history == [
        {"role": "user", "content": "My name is Sam."},
        {"role": "assistant", "content": "Hi Sam"},
    ]
    assert sent == [[{"role": "user", "content": "My name is Sam."}]]


def test_failed_call_leaves_the_history_unchanged(monkeypatch):
    def fail(client, model, messages):
        # The request is only used for error details, which this test does not read.
        raise APIConnectionError(request=None)  # type: ignore[arg-type]

    monkeypatch.setattr(chat, "stream_reply", fail)
    history = make_history(1)
    with pytest.raises(APIConnectionError):
        chat.take_turn(None, "model", history, "Hello?")
    assert history == make_history(1)
