---
name: feedpebble-work
description: >-
  Run the FeedPebble implementation workflow for an issue in the BenBot
  FeedPebble project (the chatbot article series, BENBOT-50 to BENBOT-60):
  fetch issue context, check blockers, confirm scope, set the started status,
  do the work, post a report comment, and move the issue to review without ever
  closing it. Use when the user invokes /feedpebble-work or asks to work on a
  FeedPebble issue such as BENBOT-51. Optional argument: issue key (BENBOT-n) or
  issue ULID.
disable-model-invocation: true
---

# FeedPebble work (bready-or-bot)

Use this when work is tied to a FeedPebble issue in the `BenBot` project. In this
repo those are the article-series issues BENBOT-50 to BENBOT-60 (code issues and
article-draft issues). Project rules, git rules, and the standard report format
are in `CLAUDE.md`. Follow them.

This repo is a git repo. Commit on `main`, never push, never branch.

## Issue reference (`$ARGUMENTS`)

Accept an issue key (preferred, such as `BENBOT-51`) or a 26-character ULID.

- If the arguments are empty and the conversation names exactly one issue, use it.
- If there are zero or several candidates, or the reference is ambiguous, ask the
  user which issue before calling FeedPebble.

Project: `BenBot` (`projectSlug: "benbot"`). If the key has another prefix or the
user names another project, use that project and do not assume BenBot.

## Steps (in order, do not skip)

1. **Fetch the issue and the briefing.** Call `get_issue_context` with
   `{ issueKey, projectSlug: "benbot" }` (or `{ issueId }`) and
   `list_project_context` for the project. Read the title, description, priority,
   all comments, and the `relations` block. Comments from Ben override matching
   lines in the description. The briefing is mostly about the BenBot app, which
   does NOT apply to this series (see `CLAUDE.md`). Note the issue ULID, key, and
   any blockers.

   1a. **Blocker gate.** Inspect `relations.blockedBy`:
   - `open` blockers: stop and surface them (key, title, status). Ask whether to
     switch to the blocker, proceed anyway, or cancel. Do not set the started
     status until the user decides. For an article issue, an unfinished code
     issue is a hard stop: the issue says not to start until it is done.
   - `in_progress` blockers: do not block. Note them in one line and continue.
   - `done` or `cancelled` blockers: satisfied, ignore.
   - Prefer the live `relations` graph over the description's prose.

2. **Summarize and confirm.** Give the user a short summary of what the issue
   asks for and which deliverables and acceptance criteria apply. Call out
   anything unverified in the issue, any comment that changes the description,
   and any question you must ask (for example a missing `.env` key: stop and ask).
   If scope is unclear, ask before working.

   2a. **Parent context (conditional).** If `relations.parent` exists and the
   issue cites it as a source of truth, fetch it once. Otherwise skip. For code
   issues that this one depends on, read their closing report comments when the
   issue says to build on them.

3. **Set the started status.** Call `list_issue_statuses` and use the `started`
   role status with the lowest sortOrder (currently `in_progress`). Only after the
   correct issue is confirmed and no blocker stop applies. Skip if already there.

   3a. **Create an agent run.** Call `mcp__claude_ai_FeedPebble__create_agent_run`
   with the project, the issue key, `state: "running"`, and a short title (issue
   key plus issue title). Keep the run id. Skip if you stopped at the blocker
   gate or are waiting on the user.

4. **Do the work.** Follow the issue's deliverables and the rules in `CLAUDE.md`:
   - Verify the facts the issue says to verify against current docs before
     writing code, and record the date.
   - Reference code is unrun: run it, fix it, and report each change.
   - Run what the acceptance criteria name (sessions, tests, `ruff check .`,
     `ruff format --check .`) and keep the real output for the report.
   - Text rules apply to everything you write: no contractions, no em dashes, no
     emojis.
   - Article issues: write only to the gitignored `drafts/`, follow your own
     article from a clean copy, and run the automated text checks.
   - If you need a design decision, post it as an issue comment and stop.

5. **Commit (code issues).** Commit on `main` with a clear message. Do not push.
   Run `git status` and `git branch` and keep both outputs. Search the commit for
   the key prefix `sk-or-`. Article issues commit nothing; confirm `git status`
   does not show the draft.

6. **Post the report.** Use `add_issue_comment` with the standard report from
   `CLAUDE.md`: summary, files changed, exact commands with real output,
   deviations, unverified items, questions, plus whatever the issue's "Report
   back" section adds. If `relations.blocks` is non-empty, say which downstream
   issues this unblocks (key and title) once verified. Write for a human reviewer
   and never include a key.

7. **Set the review status.** Look up `list_issue_statuses` and move the issue to
   `ready_for_qa` (the project's review state; if it is renamed or missing, pick
   the equivalent and say so). Never set `done` or `cancelled`, and do not set
   `open` unless the user asks. Ben closes issues.

8. **Finish the agent run.** Call `mcp__claude_ai_FeedPebble__update_agent_run`
   with the run id from step 3a:
   - Work complete: `state: "succeeded"` and a short `summary`. Add `externalUrl`
     only if a pull request was opened (not expected here).
   - You started the run and stopped because work or a check failed:
     `state: "failed"` and a non-empty `error`.
   - Do not leave the run `running`. If you stopped to ask a design question,
     report the run as failed with the question as the error, or leave the issue
     in its started status and tell the user why.

## Relations (optional)

When work spawns a follow-up issue, link it with `relate_issues`
(`parent_of`, `relates_to`, `blocks`). Use `list_issue_relations` to inspect.
