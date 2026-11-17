# Part 1: Basic bot setup

> **Learning project.** This code is written to teach concepts. It is not hardened for production. Anything you put in front of real users needs proper security, testing, and monitoring first.

Article: coming soon.

## What you will build

The smallest possible chatbot. You type a message, the program sends it to a model through OpenRouter, prints the reply, and asks for the next message. It also prints how many tokens each exchange used.

There is deliberately no conversation memory. Each message is sent alone, so the bot cannot remember anything you said earlier. Part 2 fixes that.

## How to run it

Run these from the root of the repo. You need Python 3.11 or newer and an OpenRouter API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r part-1/requirements.txt
cp part-1/.env.example part-1/.env
# edit part-1/.env and replace your-key-here with your OpenRouter key
python part-1/chat.py
```

Type a message and press Enter. Type `quit` or `exit`, or press Ctrl+D or Ctrl+C, to leave.

The settings live in `.env`:

| Setting | Meaning |
|---|---|
| `LLM_BASE_URL` | The OpenAI-compatible API address. The default is OpenRouter. |
| `LLM_API_KEY` | Your API key. Never commit it. |
| `LLM_MODEL` | The model name. Pick any chat model from https://openrouter.ai/models. |

If the service fails (a wrong key, an unknown model, no credit, or no network), the bot prints one short error line and waits for your next message.

## What changed since the last part

Nothing. This is where we start.
