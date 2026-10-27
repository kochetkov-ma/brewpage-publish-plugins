---
name: brewpage-publish
description: Publish text, Markdown, JSON, files, or built static sites to BrewPage and return a shareable URL. Use when asked to publish, upload, host, or share content with BrewPage.
user-invocable: true
disable-model-invocation: false
---

# BrewPage publishing

Read `upstream/SKILL.md` completely before acting. It contains the existing publishing workflow, security constraints, consent choices, archive review, and exact command arguments. Its seven-file implementation is preserved unchanged from the MIT-licensed upstream skill.

Apply these DeepSeek Harness translations while following that workflow:

- Resolve `${CLAUDE_SKILL_DIR}` to the absolute `upstream` directory beside this file. Resolve `$ARGUMENTS` to the user's actual request. Never expect these Claude variables to exist in the shell.
- Use the current Harness's native file read, search, shell, and user-question tools for the upstream names `Read`, `Glob`, `Bash`, and `AskUserQuestion`. A normal chat question is valid if no structured question tool exists. Missing tools or answers block the dependent action.
- Claude `model`, tool allowlists, and pre-approval claims are not Harness settings. Follow the Harness permission system and never bypass its approval prompts. Preserve the upstream single-command argument escaping and length limits.
- Namespace and password choices require explicit answers before upload; preserve archive confirmation, owner-token secrecy and exact returned URLs.
- For EVERY upstream command, replace `bash ${CLAUDE_SKILL_DIR}/scripts/brewpage-run.sh` with `python3 '/absolute/native/skill/scripts/brewpage-native.py'`, resolving that adapter beside this file. Keep all following arguments unchanged. Never invoke the upstream helper directly.
- The adapter resolves relative input and password-file paths before using its own private working directory. History is isolated at `~/.dsh/brewpage-publish/.claude/brewpage-history.md` (mode 600); report that exact native path. Never read, copy or write a project's or another runtime's Claude history or authentication.
- Input, probe and password paths with `.claude` or `.claude-*` components are forbidden case-insensitively, including aliases resolving there. The helper receives only minimal environment variables, private temporary storage and isolated Git settings.
- The accompanying MCP server is available for separate explicitly requested MCP work; it does not replace or weaken this skill's consent and secure history workflow.

Do not load upstream Claude metadata as a second skill or copy authentication from another client.
