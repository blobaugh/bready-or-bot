# Part 4: Giving the bot knowledge with RAG

> **Learning project.** This code is written to teach concepts. It is not hardened for production. Anything you put in front of real users needs proper security, testing, and monitoring first.

Article: coming soon.

Bready or Not is a fictional bakery, and Port Gallant is a fictional town. All of the content in `content/` is made up. Nothing here describes a real business, and the allergen notes are not real allergen advice.

## What you will build

The Part 3 chatbot, with knowledge. Crumb now answers questions about the bakery from four markdown documents, using retrieval-augmented generation (RAG) written in plain Python.

- **Chunking.** Each document is split into passages (chunks) at its `## ` headings. One vector for a whole document is too blurry to match a specific question.
- **Embeddings.** An embedding model turns a piece of text into a long list of numbers, called a vector. Texts with similar meaning get vectors that point in similar directions. The embedding model is only a lookup tool. It does not train or change the chat model.
- **Cosine similarity.** A number that says how closely two vectors point the same way. Higher means more related. Scores are not probabilities, so a low score does not mean "no answer".
- **Retrieval.** For each question, the bot embeds the question, scores every chunk, and takes the top three. Those chunks are placed in the request next to the question.

There is no vector database and no framework. The index is one JSON file, `index.json`, that you can open and read.

## How to run it

Run these from the root of the repo. You need Python 3.11 or newer and an OpenRouter API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r part-4/requirements.txt
cp part-4/.env.example part-4/.env
# edit part-4/.env and replace your-key-here with your OpenRouter key
python part-4/ingest.py
python part-4/chat.py
```

`ingest.py` reads every `.md` file in `content/`, embeds the chunks, and writes `index.json`. Run it once, and again whenever the content changes. It prints how many files and chunks it processed. The index is generated on your machine and is not committed.

To see retrieval on its own, without the chat model:

```bash
python part-4/retrieve.py "What time do you close on Friday?"
```

To see what the chat bot retrieves for each question, start it with the debug flag:

```bash
python part-4/chat.py --debug
```

If `index.json` is missing, or it was built with a different `EMBED_MODEL`, the chat exits and tells you to run `ingest.py`.

The settings live in `.env`:

| Setting | Meaning |
|---|---|
| `LLM_BASE_URL` | The OpenAI-compatible API address. The default is OpenRouter. |
| `LLM_API_KEY` | Your API key. Never commit it. |
| `LLM_MODEL` | The chat model name. Pick any chat model from https://openrouter.ai/models. |
| `LLM_TEMPERATURE` | Optional. A number from 0 to 2. Blank or unset means 0.3. |
| `EMBED_MODEL` | The embedding model. The default is `openai/text-embedding-3-small`. |

The chat model and the embedding model use the same base URL and key.

## Add your own content

Put markdown files in `content/` and run `python part-4/ingest.py` again. Each file should start with a `# ` title, and each topic should sit under its own `## ` heading. Text before the first `## ` heading and sections with no text are skipped. Delete the sample files if you want only your own.

## What to expect

- Each request carries the three best chunks, always. There is no score cut-off, so an off-topic question still gets three chunks, and the system prompt has to handle it.
- The history keeps only the plain question. The retrieved chunks are added to the request for the current turn only, so the history stays small.
- Retrieval looks only at the newest question. A follow-up such as "And on Sunday?" has little meaning on its own and may retrieve poorly.
- A small model can still ignore its instructions and make something up, even when the chunks do not contain the answer.

## How to run the tests

The tests cover chunking, ranking with hand-made vectors, and message assembly. They need no network and no API key.

```bash
pip install -r part-4/requirements-dev.txt
pytest part-4
ruff check .
ruff format --check .
```

## What changed since the last part

- New: `content/`, four markdown documents about the fictional bakery.
- New: `ingest.py`, which chunks the documents, embeds the chunks, and writes `index.json`.
- New: `retrieve.py`, which scores every chunk against a question and returns the best ones. It also runs by itself.
- `chat.py` retrieves the top three chunks before each model call and builds the user message from the chunks plus the question. It has a `--debug` flag and checks the index at startup.
- `system_prompt.md`: rule 3 now says to answer only from the bakery's documents that come with each question.
- `.env.example` has the new `EMBED_MODEL` line, and `requirements.txt` adds `numpy`.
- New: `tests/test_retrieval.py`. The earlier tests are updated for the new `take_turn()` arguments.
