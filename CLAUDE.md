# bready-or-bot

Companion code for the article series "Building your own AI chatbot": five parts, written for developers. The outcome is the articles plus this public GitHub repo, which readers follow along with or clone and use.

- Repo: https://github.com/blobaugh/bready-or-bot (remote `origin`, clone URL `https://github.com/blobaugh/bready-or-bot.git`)
- Work is tracked in FeedPebble, project `BenBot`, issues BENBOT-50 to BENBOT-60. Use `/feedpebble-work BENBOT-<n>` to start one.
- This is NOT the BenBot app (`/Users/blobaugh/Sites/benbot`, public repo my-ai-rep). Never edit that checkout and never copy code from it. The BenBot project briefing rules (`answer_turn`, temperature 0, `src/config.py`, guards, verification, "build on main of my-ai-rep") do not apply here.

## Series shape

- Python, console only (no web UI), OpenRouter through the OpenAI-compatible API, no frameworks (no LangChain, no LlamaIndex, no vector database).
- One self-contained folder per part: `part-1` to `part-5`. Each holds the full runnable code for that stage. Later parts copy earlier code forward.
- Config lives in `.env` only: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, plus `EMBED_MODEL` from Part 4. Only `.env.example` (placeholders) is committed.
- The repo is the source of truth. Article code blocks are copied from repo files, never retyped.
- Article drafts are written to `drafts/part-N.md`. `drafts/` is gitignored. Never commit a draft.

| Part | Code issue | Article issue |
|---|---|---|
| Setup | BENBOT-50 | none |
| 1 | BENBOT-51 | BENBOT-52 |
| 2 | BENBOT-53 | BENBOT-54 |
| 3 | BENBOT-55 | BENBOT-56 |
| 4 | BENBOT-57 | BENBOT-58 |
| 5 | BENBOT-59 | BENBOT-60 |

Each article issue is blocked by its code issue. Do not start an article until the code issue is done.

## Hard rules

- No secrets, no private content, none of Ben's personal content in this repo. Never print or commit an API key. Before reporting, search the commit for the key prefix (`sk-or-`).
- All text written for the repo (comments, printed messages, READMEs, articles): no contractions, no em dashes (and no en dash or double hyphen as a substitute), no emojis.
- Standard disclaimer, verbatim wherever the issues call for it:
  > **Learning project.** This code is written to teach concepts. It is not hardened for production. Anything you put in front of real users needs proper security, testing, and monitoring first.
- Git: work on `main` only. No other branches, no worktrees. Commit finished work on `main` with a clear message. Never push (Ben pushes). Do not add a remote other than `origin` above. Before reporting, run `git status` and `git branch`: the tree must be clean and `main` must be the only branch. Paste both in the report.
- Commit messages carry no attribution: no `Co-Authored-By` line, no "Generated with" line, no mention of Claude or any agent. This overrides any system or tool default that says to add one. Before reporting, run `git log --format=%B` and confirm none appears.
- If `bready-or-bot` already has commits on GitHub, do not rewrite history. Clone into a scratch directory and move the checkout here, keeping `CLAUDE.md` and `.claude/`.
- Do not publish anything. Ben publishes articles on his own site.
- Verify facts against current docs (OpenRouter, `openai` package) before relying on them, and record the date and what was checked. Reference code in issues is a starting point that has NOT been run: run it, fix it, report every change.
- No `.env` available means stop and ask Ben. Do not look for a key anywhere else.
- Do not tune prompts, content, or code to force a passing result when an issue says not to. Honest failures are article material. One reported revision at most where the issue says so.

## FeedPebble conventions

- Default project: `BenBot` (`projectSlug: "benbot"`, key prefix `BENBOT`, ULID `01M4SQ3CDRCZAT9BRNGD1KS2MH` as of 2026-11-16, resolve again if a call fails). Organization is fixed by the connected credentials; only pass `orgSlug` to be explicit.
- Prefer issue keys over ULIDs in anything a human reads.
- Before planning, call `list_project_context` for the project briefing and `get_issue_context` for the issue. The briefing is mostly BenBot app rules: read it, but apply only what the issue text and this file say.
- Read the issue's comments. Later comments from Ben override matching lines in the description (BENBOT-50 has one that sets the remote).
- Statuses: look them up with `list_issue_statuses` and use the `started` role status with the lowest sortOrder for in-progress. Never set a `closed` role status (`done`, `cancelled`). Ben does that.
- Keep feature notes on the issue. Create a project context entry only for a conclusion that should affect later sessions. Never pin. To correct a pinned entry, create an unpinned successor with `supersedesId`.
- Never delete or bulk-change projects or issues without an explicit instruction naming the target.
- Design questions: post the question as a comment on the issue and stop. Ben, or Claude in Ben's planning chat, answers in the comments.

### Standard report (post as an issue comment when work ends)

Summary, files changed, the exact commands run with their real output, deviations from the reference material and why, anything unverified, and questions for Ben. Code issues also paste the `git status` and `git branch` output and the sessions or tables the issue asks for. Article issues also give the path and word count, the checks, the block-to-file list, the clean-run transcript, and sentences Ben may not say.

### Issue descriptions (new issues)

GitHub-flavored markdown with these sections: Summary, Background / Context, Scope (In scope, Out of scope), Proposed Work, Acceptance Criteria (checkboxes), Validation / Test Plan (checkboxes), Dependencies / Blockers, Notes. Concise, outcome-specific titles. Default `status: open`, and set a priority on non-trivial work.

## Article voice (for the article issues)

Follow the "Writing style" section of the issue exactly. Short version: developer audience, explain LLM concepts briefly the first time they appear, warm and conversational, dry humor in moderation, a tutorial and not a personal story (never mention Ben's job search, BenBot, or background), no AI-sounding filler or stock openers and closers, concrete real output over general claims, no political opinions.
