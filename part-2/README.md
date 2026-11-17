# Part 2: Adding chat history

> **Learning project.** This code is written to teach concepts. It is not hardened for production. Anything you put in front of real users needs proper security, testing, and monitoring first.

Article: coming soon.

## What you will build

The Part 1 chatbot, extended in three ways:

- **Memory.** The program keeps a list of every message and sends the whole list with each request. The model itself still remembers nothing between calls.
- **Streaming.** The reply appears piece by piece as the model produces it, instead of all at once at the end.
- **Trimming.** Only the most recent messages are sent, so the request does not grow without limit. The price is that the bot forgets whatever fell off the front.

The token line after each reply shows the memory cost directly: the input count rises with every turn, because every earlier message is sent again.

## How to run it

Run these from the root of the repo. You need Python 3.11 or newer and an OpenRouter API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r part-2/requirements.txt
cp part-2/.env.example part-2/.env
# edit part-2/.env and replace your-key-here with your OpenRouter key
python part-2/chat.py
```

Type a message and press Enter. Type `reset` to clear the conversation, and `quit` or `exit`, or press Ctrl+D or Ctrl+C, to leave.

The settings are the same as in Part 1 and live in `.env`:

| Setting | Meaning |
|---|---|
| `LLM_BASE_URL` | The OpenAI-compatible API address. The default is OpenRouter. |
| `LLM_API_KEY` | Your API key. Never commit it. |
| `LLM_MODEL` | The model name. Pick any chat model from https://openrouter.ai/models. |

## How to run the tests

The tests cover the trimming and the history handling. They need no network and no API key.

```bash
pip install -r part-2/requirements-dev.txt
pytest part-2
ruff check .
ruff format --check .
```

## How the history is trimmed

`MAX_HISTORY_MESSAGES` in `chat.py` is how many saved messages are sent with each request, along with the new question. The default is 20, which is ten question and answer pairs. Change it and run the bot again to see the effect. A value of 4 makes the bot forget a name you told it after a couple of turns.

Keep the limit even. The saved history is whole question and answer pairs, so an even limit means the trimmed list always starts with a user message.

A question and its reply are saved only after the reply arrives. If a request fails, the history is left as it was, so it never holds two user messages in a row.

Idea for later, not built here: instead of dropping old messages, ask the model to write a short summary of them and send the summary in their place. The bot would keep the gist of what it would otherwise forget.

## What changed since the last part

- `chat.py` keeps a `history` list and sends it with every request.
- Replies are streamed with `stream=True`. The token counts arrive on the last chunk of the stream, and the token line is printed after each reply.
- `trim_history()` limits how much of the saved history is sent.
- A `reset` command clears the history.
- New: `tests/test_history.py`, `requirements-dev.txt`, and `conftest.py` (which lets the tests import `chat.py`).
