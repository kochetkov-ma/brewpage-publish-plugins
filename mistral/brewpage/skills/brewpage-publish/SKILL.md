---
name: brewpage-publish
description: Host HTML pages and static sites, publish AI artifacts, and share Markdown, documents, reports or any file with BrewPage. Load when asked to publish, upload, host or share content and create a hosted link.
user-invocable: true
disable-model-invocation: false
license: MIT
---

# BrewPage publishing compatibility adapter

Read `upstream/SKILL.md` relative to this skill's base directory before proceeding. Follow that existing workflow, its validation, explicit namespace/password choices, archive review digest, secure token handling and result rules. The seven files under `upstream/` are the unchanged implementation; do not replace or duplicate them.

Apply only these host translations:

- Use Vibe's available file-reading/search tools for `Read`/`Glob`, its shell execution tool for `Bash`, and its user-question tool or ordinary conversation for `AskUserQuestion`. Wait for explicit answers; an unavailable question tool or silence never authorizes publishing.
- Treat invocation text as `$ARGUMENTS`. Replace every `bash ${CLAUDE_SKILL_DIR}/scripts/brewpage-run.sh` prefix with `python3 '<absolute skill base directory>/run.py'`. Keep the original subcommand and arguments. Resolve every content or password file path to an absolute path before invocation. Never execute the upstream runner directly.
- The launcher runs the original secure runner in a private Mistral state directory and strips inherited Claude/Git environment. Keep the original single-quote escaping for every value, command length limit and one-command rule. Vibe's normal approvals apply; Claude permission hints and `model: haiku` do not configure Vibe.

History belongs only to `$VIBE_HOME/brewpage-publish-state/.claude/brewpage-history.md` (default `~/.vibe/brewpage-publish-state/.claude/brewpage-history.md`). Report that location instead of the upstream project-root path. Never read or display any history or owner token, access existing Claude state, or copy authentication between runtimes. Do not substitute direct HTTP or MCP publishing for this skill's runner: MCP tools are available separately, but bypassing the runner bypasses this workflow's archive and history safeguards.
