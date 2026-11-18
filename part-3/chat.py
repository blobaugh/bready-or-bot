"""Part 3: a chatbot with a job and a personality, set by a system prompt."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

REQUIRED_SETTINGS = ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")

# Lower values make replies more predictable. A customer-facing assistant wants it fairly low.
DEFAULT_TEMPERATURE = 0.3

SYSTEM_PROMPT_FILE = Path(__file__).parent / "system_prompt.md"

# How many saved messages are sent with each request, plus the new question. Keep this even:
# saved history is whole question and answer pairs, so the trimmed list starts with a user message.
MAX_HISTORY_MESSAGES = 20

Message = dict[str, str]

STATUS_HINTS = {
    400: "The service rejected the request. Check that LLM_MODEL is a valid model name.",
    401: "The API key was rejected. Check LLM_API_KEY in .env.",
    402: "The account is out of credit.",
    404: "The model was not found. Check LLM_MODEL in .env.",
    429: "Rate limited. Wait a moment and try again.",
}


def read_temperature() -> float:
    """Read LLM_TEMPERATURE. Use the default when it is unset or blank."""
    raw = os.environ.get("LLM_TEMPERATURE", "").strip()
    if not raw:
        return DEFAULT_TEMPERATURE
    try:
        return float(raw)
    except ValueError:
        sys.exit(f"LLM_TEMPERATURE in .env must be a number, not {raw!r}.")


def load_settings() -> dict[str, str]:
    """Read settings from .env and stop early if one is missing."""
    load_dotenv()
    missing = [name for name in REQUIRED_SETTINGS if not os.environ.get(name)]
    if missing:
        sys.exit(f"Missing settings in .env: {', '.join(missing)}")
    return {name: os.environ[name] for name in REQUIRED_SETTINGS}


def load_system_prompt() -> Message:
    """Read the system prompt file and return it as a system message."""
    text = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()
    return {"role": "system", "content": text}


def trim_history(history: list[Message], max_messages: int = MAX_HISTORY_MESSAGES) -> list[Message]:
    """Return only the most recent saved messages, so the request stays a sensible size."""
    return history[-max_messages:]


def build_messages(system_message: Message, history: list[Message]) -> list[Message]:
    """The system prompt always goes first. Only the conversation is trimmed."""
    return [system_message] + trim_history(history)


def stream_reply(
    client: OpenAI, model: str, messages: list[Message], temperature: float
) -> tuple[str, int, int]:
    """Print the reply as it arrives. Return the full text and the token counts."""
    stream = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature, stream=True
    )
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
    client: OpenAI,
    model: str,
    system_message: Message,
    temperature: float,
    history: list[Message],
    question: str,
) -> tuple[int, int]:
    """Stream the reply, then remember the question and the reply.

    If the model call fails, the history is left unchanged.
    """
    messages = build_messages(system_message, history) + [{"role": "user", "content": question}]
    print("Crumb: ", end="", flush=True)
    reply, prompt_tokens, completion_tokens = stream_reply(client, model, messages, temperature)
    history.append({"role": "user", "content": question})
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
    temperature = read_temperature()
    system_message = load_system_prompt()
    history: list[Message] = []

    print(f"Chatting with Crumb ({model}, temperature {temperature}).")
    print("Type 'reset' to forget the conversation, 'quit' to exit.")
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
            prompt_tokens, completion_tokens = take_turn(
                client, model, system_message, temperature, history, question
            )
        except (APIConnectionError, APIStatusError) as error:
            print(f"\nError: {describe_error(error)}")
            continue
        print(f"[tokens: {prompt_tokens} in, {completion_tokens} out]")


if __name__ == "__main__":
    main()
