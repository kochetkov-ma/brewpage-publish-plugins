---
name: brewpage-publish
description: Host HTML pages and static sites, publish AI artifacts, and share Markdown, documents, reports or any file with BrewPage. Load when asked to publish, upload, host or share content and create a hosted link.
user-invocable: true
disable-model-invocation: false
license: MIT
---

# BrewPage publishing compatibility adapter

Read [the bundled workflow](upstream/SKILL.md) before acting. Its recipes are under `upstream/references/`. Resolve recipe links from the file that links them, and use the [publishing](upstream/references/publishing.md) and [ownership](upstream/references/ownership.md) instructions when the workflow calls for them.

Apply only these host translations:

- Use Vibe's file-reading and search tools for `Read` and `Glob`, its shell tool for `Bash`, and its question tool or ordinary conversation for `AskUserQuestion`. Obtain explicit namespace and password choices before upload.
- Treat invocation text as `$ARGUMENTS`. Replace each `bash {runner}` in a recipe, or the equivalent expanded upstream shell invocation, with `python3 '<absolute skill base directory>/run.py'`. Keep the runner subcommand and arguments. Resolve all input and protected file paths to absolute paths. Run upstream commands through this launcher.
- The launcher uses a private Mistral state directory and strips the inherited Claude and Git environment. Keep the recipe's single-quote escaping, command length limit and one-command rule. Follow Vibe's normal approvals.

Return the exact reader link and relevant notices. Include a returned management link only when both tool output and chat are verified owner-only. Use `--private-output` only in that context. Native history is `$VIBE_HOME/brewpage-publish-state/.claude/brewpage-history.md` (default `~/.vibe/brewpage-publish-state/.claude/brewpage-history.md`) with a sibling recovery receipt. Report a saved key only after the runner verifies storage. Follow the ownership recipe for recovery and keep private capability values and storage paths in an owner-only channel. Do not access existing Claude state or copy authentication between runtimes.

Before a write, prefer an exposed BrewPage MCP operation with the required options, selected owner authority and verified private delivery of any credential-bearing result. Choose the isolated launcher before dispatch when the MCP path lacks those capabilities or cannot handle the local bytes. Keep the same owner authority and Vibe approvals. A failed or refused write stays on its selected route, and an ambiguous result needs reconciliation before another write.
