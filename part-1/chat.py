"""Part 1: the simplest possible chatbot. One message in, one reply out."""

import os
import sys

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

REQUIRED_SETTINGS = ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")

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


def ask(client: OpenAI, model: str, question: str) -> tuple[str, int, int]:
    """Send one message to the model. Return the reply and the token counts."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
    )
    reply = response.choices[0].message.content or ""
    usage = response.usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    return reply, prompt_tokens, completion_tokens


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

    print(f"Chatting with {model}. Type 'quit' to exit.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        try:
            reply, prompt_tokens, completion_tokens = ask(client, model, question)
        except (APIConnectionError, APIStatusError) as error:
            print(f"Error: {describe_error(error)}")
            continue
        print(f"Bot: {reply}")
        print(f"[tokens: {prompt_tokens} in, {completion_tokens} out]")


if __name__ == "__main__":
    main()
