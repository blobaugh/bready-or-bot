# Part 3: Giving the bot a personality with a system prompt

> **Learning project.** This code is written to teach concepts. It is not hardened for production. Anything you put in front of real users needs proper security, testing, and monitoring first.

Article: coming soon.

Bready or Not is a fictional bakery, and Port Gallant is a fictional town. Nothing here describes a real business.

## What you will build

The Part 2 chatbot, with a job. It becomes **Crumb**, the AI assistant for Bready or Not. The job, the tone, and the rules live in a plain text file, `system_prompt.md`, which is sent as the first message of every request.

- **A system prompt.** A message with the role `system`, placed first in the list. It tells the model who it is, who it is talking to, how to sound, and what the rules are.
- **Basic guardrails in the prompt.** Stay on topic, do not invent facts, say when you do not know, and make no promises for the business.
- **A temperature setting.** A sampling setting. Lower values make replies more predictable, and higher values make them more varied.

Be careful with one idea: instructions are requests, not locks. A model usually follows its system prompt, but it is not guaranteed to, and a small, cheap model follows it less reliably than a large one. At this stage Crumb also knows nothing about the bakery, such as its hours or prices. A good answer is "I do not know that yet". Try it and see what you get. Part 4 adds the knowledge.

## How to run it

Run these from the root of the repo. You need Python 3.11 or newer and an OpenRouter API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r part-3/requirements.txt
cp part-3/.env.example part-3/.env
# edit part-3/.env and replace your-key-here with your OpenRouter key
python part-3/chat.py
```

Type a message and press Enter. Type `reset` to clear the conversation, and `quit` or `exit`, or press Ctrl+D or Ctrl+C, to leave.

The settings live in `.env`:

| Setting | Meaning |
|---|---|
| `LLM_BASE_URL` | The OpenAI-compatible API address. The default is OpenRouter. |
| `LLM_API_KEY` | Your API key. Never commit it. |
| `LLM_MODEL` | The model name. Pick any chat model from https://openrouter.ai/models. |
| `LLM_TEMPERATURE` | Optional. A number from 0 to 2. Blank or unset means 0.3. |

## Change the prompt

Open `system_prompt.md`, edit it, and start the bot again. The file is read once at startup. Try removing a rule to see what changes, or change the tone line.

The system message is kept apart from the saved history. Each request is built as `[system_message] + trim_history(history)`, so trimming can drop old conversation but never the prompt.

## How to run the tests

The tests cover the history handling, the system message position, and the temperature setting. They need no network and no API key.

```bash
pip install -r part-3/requirements-dev.txt
pytest part-3
ruff check .
ruff format --check .
```

## What changed since the last part

- New: `system_prompt.md`, the job description for Crumb.
- `chat.py` loads the prompt at startup with `load_system_prompt()` and sends it first on every request through `build_messages()`.
- `chat.py` reads an optional `LLM_TEMPERATURE` setting (default 0.3) and passes it as `temperature=` on each request.
- `.env.example` has the new `LLM_TEMPERATURE` line.
- New: `tests/test_system_prompt.py`. The Part 2 tests in `tests/test_history.py` still pass, with small updates for the new function signatures.
