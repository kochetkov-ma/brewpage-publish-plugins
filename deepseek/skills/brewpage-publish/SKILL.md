---
name: brewpage-publish
description: Host HTML pages and static sites, publish AI artifacts, and share Markdown, documents, reports or any file with BrewPage. Use when asked to publish, upload, host, or share content with BrewPage.
user-invocable: true
disable-model-invocation: false
---

# BrewPage publishing

Read [the bundled workflow](upstream/SKILL.md) before acting. Its recipes are under `upstream/references/`. Resolve recipe links from the file that links them, and use the [publishing](upstream/references/publishing.md) and [ownership](upstream/references/ownership.md) instructions when the workflow calls for them.

Apply these DeepSeek Harness translations while following that workflow:

- Resolve `${CLAUDE_SKILL_DIR}` to the absolute `upstream` directory beside this file. Resolve `$ARGUMENTS` to the user's actual request. Never expect these Claude variables to exist in the shell.
- Use the current Harness's native file read, search, shell, and user-question tools for the upstream names `Read`, `Glob`, `Bash`, and `AskUserQuestion`. A normal chat question is valid if no structured question tool exists. Missing tools or answers block the dependent action.
- Claude `model`, tool allowlists, and pre-approval claims are not Harness settings. Follow the Harness permission system and never bypass its approval prompts. Preserve the upstream single-command argument escaping and length limits.
- Obtain explicit namespace and password choices before upload. Follow the recipe's digest approval and return the exact reader link and relevant notices. Include a returned management link only when both tool output and chat are verified owner-only. Use `--private-output` only in that context. A storage failure follows the ownership recipe's protected recovery commands.
- Replace each `bash {runner}` in a recipe, or the equivalent expanded upstream shell invocation, with `python3 '/absolute/native/skill/scripts/brewpage-native.py'`. Resolve the adapter beside this file and keep the runner subcommand and arguments. Use absolute paths for protected inputs. Run upstream commands through this adapter.
- Native history is `~/.dsh/brewpage-publish/.claude/brewpage-history.md` (mode `0600`) with a sibling recovery receipt. Report a saved key only after the runner verifies storage. Keep the storage path and private capability values in an owner-only channel. Do not read, copy or write a project's or another runtime's Claude history or authentication.
- Content, probe and password paths with `.claude` or `.claude-*` components are forbidden case-insensitively, including aliases resolving there. The helper receives minimal environment variables, private temporary storage and isolated Git settings.
- Before a write, prefer an exposed BrewPage MCP operation with the required options, selected owner authority and verified private delivery of any credential-bearing result. Choose the isolated native runner before dispatch when the MCP path lacks those capabilities or cannot handle the local bytes. Keep the same owner authority and host approvals. A failed or refused write stays on its selected route, and an ambiguous result needs reconciliation before another write.

Do not load upstream Claude metadata as a second skill or copy authentication from another client.
