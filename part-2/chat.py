"""Part 2: a chatbot that remembers the conversation and streams its replies."""

import os
import sys

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

REQUIRED_SETTINGS = ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")

# The most recent messages sent with each request. Keep this an even number so a full
# conversation is whole question and answer pairs. trim_history() covers the odd case.
MAX_HISTORY_MESSAGES = 20

STATUS_HINTS = {
    400: "The service rejected the request. Check that LLM_MODEL is a valid model name.",
    401: "The API key was rejected. Check LLM_API_KEY in .env.",
    402: "The account is out of credit.",
    404: "The model was not found. Check LLM_MODEL in .env.",
    429: "Rate limited. Wait a moment and try again.",
}


def load_settings() -> dict[str, str]:
    """Read settings from .env and stop early if one is missing."""
    load_dotenv()
    missing = [name for name in REQUIRED_SETTINGS if not os.environ.get(name)]
    if missing:
        sys.exit(f"Missing settings in .env: {', '.join(missing)}")
    return {name: os.environ[name] for name in REQUIRED_SETTINGS}


def trim_history(
    history: list[dict[str, str]], max_messages: int = MAX_HISTORY_MESSAGES
) -> list[dict[str, str]]:
    """Return only the most recent messages, so the request stays a sensible size."""
    trimmed = history[-max_messages:]
    # The newest message is the user's question, so the list usually has an odd length and
    # the cut can land on an assistant reply. Drop it so the list starts with a user message.
    if trimmed and trimmed[0]["role"] == "assistant":
        trimmed = trimmed[1:]
    return trimmed


def stream_reply(
    client: OpenAI, model: str, messages: list[dict[str, str]]
) -> tuple[str, int, int]:
    """Print the reply as it arrives. Return the full text and the token counts."""
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    parts: list[str] = []
    prompt_tokens = 0
    completion_tokens = 0
    for chunk in stream:
        # The token counts arrive on the last chunk, so look at every chunk for them.
        if chunk.usage:
            prompt_tokens = chunk.usage.prompt_tokens
            completion_tokens = chunk.usage.completion_tokens
        if not chunk.choices:
            continue
        text = chunk.choices[0].delta.content or ""
        print(text, end="", flush=True)
        parts.append(text)
    print()
    return "".join(parts), prompt_tokens, completion_tokens


def take_turn(
    client: OpenAI, model: str, history: list[dict[str, str]], question: str
) -> tuple[int, int]:
    """Add the question to the history, stream the reply, and add the reply too.

    If the model call fails, the question is removed again, so the history never holds
    two user messages in a row. The error is passed on to the caller.
    """
    history.append({"role": "user", "content": question})
    print("Bot: ", end="", flush=True)
    try:
        reply, prompt_tokens, completion_tokens = stream_reply(client, model, trim_history(history))
    except (APIConnectionError, APIStatusError):
        history.pop()
        print()
        raise
    history.append({"role": "assistant", "content": reply})
    return prompt_tokens, completion_tokens


def describe_error(error: Exception) -> str:
    """Turn an API failure into one short line. Never include the key."""
    if isinstance(error, APIConnectionError):
        return "Could not reach the service. Check your network and LLM_BASE_URL."
    if isinstance(error, APIStatusError):
        default = f"The service returned an error (status {error.status_code})."
        return STATUS_HINTS.get(error.status_code, default)
    return "Something went wrong talking to the service."


def main() -> None:
    settings = load_settings()
    client = OpenAI(base_url=settings["LLM_BASE_URL"], api_key=settings["LLM_API_KEY"])
    model = settings["LLM_MODEL"]
    history: list[dict[str, str]] = []

    print(f"Chatting with {model}. Type 'reset' to forget the conversation, 'quit' to exit.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit"}:
            break
        if question.lower() == "reset":
            history.clear()
            print("Conversation cleared.")
            continue
        if not question:
            continue
        try:
            prompt_tokens, completion_tokens = take_turn(client, model, history, question)
        except (APIConnectionError, APIStatusError) as error:
            print(f"Error: {describe_error(error)}")
            continue
        print(f"[tokens: {prompt_tokens} in, {completion_tokens} out]")


if __name__ == "__main__":
    main()
