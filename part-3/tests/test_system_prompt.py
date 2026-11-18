"""Tests for the system prompt and the temperature setting. No network and no API key needed."""

import chat
import pytest

SYSTEM = {"role": "system", "content": "You are Crumb."}


def make_history(pairs: int) -> list[chat.Message]:
    history: list[chat.Message] = []
    for i in range(pairs):
        history.append({"role": "user", "content": f"question {i}"})
        history.append({"role": "assistant", "content": f"answer {i}"})
    return history


def test_messages_start_with_the_system_message_for_an_empty_history():
    assert chat.build_messages(SYSTEM, []) == [SYSTEM]


def test_messages_start_with_the_system_message_after_trimming():
    history = make_history(chat.MAX_HISTORY_MESSAGES)
    messages = chat.build_messages(SYSTEM, history)
    assert messages[0] == SYSTEM
    assert messages[1:] == chat.trim_history(history)
    assert [m for m in messages if m["role"] == "system"] == [SYSTEM]


def test_the_system_message_survives_a_history_much_longer_than_the_limit():
    history = make_history(chat.MAX_HISTORY_MESSAGES * 3)
    messages = chat.build_messages(SYSTEM, history)
    assert messages[0] == SYSTEM
    assert len(messages) == chat.MAX_HISTORY_MESSAGES + 1


def test_the_request_sent_to_the_model_starts_with_the_system_message(monkeypatch):
    sent = []

    def fake_stream(client, model, messages, temperature):
        sent.append((messages, temperature))
        return "ok", 1, 1

    monkeypatch.setattr(chat, "stream_reply", fake_stream)
    history = make_history(chat.MAX_HISTORY_MESSAGES)
    chat.take_turn(None, "model", SYSTEM, 0.5, history, "One more question")
    messages, temperature = sent[0]
    assert messages[0] == SYSTEM
    assert messages[-1] == {"role": "user", "content": "One more question"}
    assert temperature == 0.5


def test_the_system_prompt_file_loads_as_a_system_message():
    message = chat.load_system_prompt()
    assert message["role"] == "system"
    assert message["content"].startswith("You are Crumb")


def test_temperature_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("LLM_TEMPERATURE", raising=False)
    assert chat.read_temperature() == chat.DEFAULT_TEMPERATURE == 0.3


@pytest.mark.parametrize("blank", ["", "   "])
def test_temperature_defaults_when_blank(monkeypatch, blank):
    monkeypatch.setenv("LLM_TEMPERATURE", blank)
    assert chat.read_temperature() == chat.DEFAULT_TEMPERATURE


def test_temperature_uses_the_value_when_set(monkeypatch):
    monkeypatch.setenv("LLM_TEMPERATURE", "0.9")
    assert chat.read_temperature() == 0.9


def test_temperature_zero_is_respected(monkeypatch):
    monkeypatch.setenv("LLM_TEMPERATURE", "0")
    assert chat.read_temperature() == 0.0


def test_temperature_that_is_not_a_number_stops_with_a_message(monkeypatch):
    monkeypatch.setenv("LLM_TEMPERATURE", "warm")
    with pytest.raises(SystemExit):
        chat.read_temperature()
