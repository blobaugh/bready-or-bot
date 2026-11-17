"""Tests for the history helpers. No network and no API key needed."""

import chat
import pytest
from openai import APIConnectionError


def make_history(count: int) -> list[dict[str, str]]:
    """Build a conversation of user and assistant messages, starting with the user."""
    roles = ["user", "assistant"]
    return [{"role": roles[i % 2], "content": f"message {i}"} for i in range(count)]


def test_short_history_is_unchanged():
    history = make_history(5)
    assert chat.trim_history(history, 20) == history


def test_long_history_keeps_only_the_newest_messages():
    history = make_history(40)
    trimmed = chat.trim_history(history, 20)
    assert len(trimmed) == 20
    assert trimmed[-1] == history[-1]


def test_trimmed_history_starts_with_a_user_message():
    # A list that ends with the newest question has an odd length. The raw cut would start
    # on an assistant reply, so the helper drops it.
    history = make_history(41)
    assert history[-1]["role"] == "user"
    trimmed = chat.trim_history(history, 20)
    assert trimmed[0]["role"] == "user"
    assert trimmed[-1] == history[-1]


def test_trim_does_not_change_the_original_list():
    history = make_history(41)
    chat.trim_history(history, 20)
    assert len(history) == 41


def test_default_limit_is_even():
    assert chat.MAX_HISTORY_MESSAGES % 2 == 0


def test_failed_call_removes_the_question(monkeypatch):
    def fail(client, model, messages):
        # The request is only used for error details, which this test does not read.
        raise APIConnectionError(request=None)  # type: ignore[arg-type]

    monkeypatch.setattr(chat, "stream_reply", fail)
    history = make_history(2)
    with pytest.raises(APIConnectionError):
        chat.take_turn(None, "model", history, "Hello?")
    assert history == make_history(2)


def test_successful_turn_adds_question_and_reply(monkeypatch):
    sent = []

    def fake_stream(client, model, messages):
        sent.append(list(messages))
        return "Hi Sam", 7, 2

    monkeypatch.setattr(chat, "stream_reply", fake_stream)
    history: list[dict[str, str]] = []
    tokens = chat.take_turn(None, "model", history, "My name is Sam.")
    assert tokens == (7, 2)
    assert history == [
        {"role": "user", "content": "My name is Sam."},
        {"role": "assistant", "content": "Hi Sam"},
    ]
    assert sent == [[{"role": "user", "content": "My name is Sam."}]]
