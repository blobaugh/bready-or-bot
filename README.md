# bready-or-bot

This is the companion code for the article series "Building your own AI chatbot". Over five parts you build a console chatbot from scratch in plain Python, with no frameworks, and each part adds one idea. The articles explain the why. This repo holds the code that runs.

Repo: https://github.com/blobaugh/bready-or-bot

> **Learning project.** This code is written to teach concepts. It is not hardened for production. Anything you put in front of real users needs proper security, testing, and monitoring first.

## The series

| Part | Title | Folder | Article |
|---|---|---|---|
| 1 | Building your own AI chatbot: Basic bot setup (Part 1) | [`part-1`](part-1) | Coming soon |
| 2 | Building your own AI chatbot: Adding chat history (Part 2) | [`part-2`](part-2) | Coming soon |
| 3 | Building your own AI chatbot: Giving the bot a personality with a system prompt (Part 3) | [`part-3`](part-3) | Coming soon |
| 4 | Building your own AI chatbot: Providing context with the RAG method (Part 4) | [`part-4`](part-4) | Coming soon |
| 5 | Building your own AI chatbot: Safety basics and what comes next (Part 5) | [`part-5`](part-5) | Coming soon |

The part folders are added as each part is finished.

## Prerequisites

- Python 3.11 or newer. Python 3.10 reaches end of life in October 2026, so 3.11 is the oldest version this series supports.
- An [OpenRouter](https://openrouter.ai) account and an API key.

## How the folders work

Each `part-N` folder is complete on its own. It holds everything that stage of the bot needs, and later parts copy the earlier code forward. You can start at any part, or follow along from Part 1.

A quick start for any part (swap in the part number you want):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r part-N/requirements.txt
cp part-N/.env.example part-N/.env
# edit part-N/.env and add your API key, then run the part as its README describes
```

The `.env` file is never committed. Only `.env.example`, which holds placeholders, lives in the repo.

## Using a different model or service

The code talks to any OpenAI-compatible API. To switch services or models, change three values in your `.env` file: `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`. Browse [openrouter.ai/models](https://openrouter.ai/models) to choose a model.

## License

MIT. See [LICENSE](LICENSE).
