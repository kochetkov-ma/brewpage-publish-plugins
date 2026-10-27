# Existing BrewPage publish skill

This package preserves all seven MIT-licensed source files from [brewpage-publish at `d2d42282fecec988447f9c9547959b31a8012644`](https://github.com/kochetkov-ma/claude-brewcode/tree/d2d42282fecec988447f9c9547959b31a8012644/skills/brewpage-publish), byte for byte.

Use the `brewpage-publish` folder where a provider accepts a skill directory, or upload `brewpage-publish.zip` where it accepts a ZIP. The ZIP opens directly to `SKILL.md`, `README.md`, `LICENSE` and `scripts/`. `manifest.json` records source and artifact hashes.

For Yandex AI Studio, use `yandex-brewpage-publish.zip`: its seven unchanged files sit inside one top-level `brewpage-publish/` folder, as required by [the official Skills documentation](https://aistudio.yandex.ru/ru/docs/ai-studio/concepts/agents/skills). The archive structure and every contained file hash were checked locally; packaging does not prove a successful native upload or execution.

For Mistral Work, `mistral-work-brewpage-publish.zip` contains an adapted root `SKILL.md` that uses the connected BrewPage MCP capabilities, a root MIT license and the unchanged seven original files under `upstream/`. The active instructions omit Claude runtime metadata and retain explicit visibility/password choices, preview, TTL, archive consent and credential privacy. Native import and execution remain separate checks. The Python skill validator could not start because PyYAML is absent; Ruby Psych parsed and checked the frontmatter instead.

The existing skill requires explicit namespace and password choices before publishing. No account or API key is required. Owner tokens stay in private local history; never paste them into chat. See the packaged skill for prerequisites and its complete workflow.

Packaging checks cover immutable source hashes, seven-file ZIP roundtrip, shell/Node/Python syntax and embedded credential patterns. No publication was made during packaging. Existing Claude Code metadata and command placeholders remain unchanged; each provider must verify its own skill discovery and execution support.
