# Existing BrewPage publish skill

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

This package preserves all seven MIT-licensed source files from [brewpage-publish at `809e0fa27793a68177d73368b9ec3bc3488e4f2e`](https://github.com/kochetkov-ma/claude-brewcode/tree/809e0fa27793a68177d73368b9ec3bc3488e4f2e/skills/brewpage-publish), byte for byte.

Use the `brewpage-publish` folder where a provider accepts a skill directory, or upload `brewpage-publish.zip` where it accepts a ZIP. The ZIP opens directly to `SKILL.md`, `README.md`, `LICENSE` and `scripts/`. `manifest.json` records source and artifact hashes.

The historical `yandex-brewpage-publish.zip` preserves the seven original Claude-oriented files in one top-level folder. Use the [portable Yandex adapter](../yandex/README.md) for a connected-MCP workflow: its eight-file archive was imported into a personal AI Studio catalog. Import and tool discovery do not prove model execution or public marketplace acceptance.

For Mistral Work, use `mistral-work-brewpage-publish-v1.0.2.zip`: it syncs `upstream/` to that commit with User-Agent `brewpage-mistral-work/1.0.2 (+https://brewpage.app)`; v1.0.1 is retained. Its root `SKILL.md` describes HTML hosting, static sites and AI artifact publishing, followed by Markdown, documents, reports and any files. This metadata-only update preserves the portable instruction body, root MIT license and seven original files under `upstream/`. The older `mistral-work-brewpage-publish.zip` remains unchanged. The active instructions retain explicit visibility/password choices, preview, TTL, archive consent and credential privacy; native import and execution remain separate checks.

The existing skill requires explicit namespace and password choices before publishing. No account or API key is required. The original Claude workflow uses private local history. Portable Work adapters preserve owner capability only through evidenced private supported storage and report a limitation otherwise; never paste credentials into chat.

Packaging checks cover immutable source hashes, seven-file ZIP roundtrip, shell/Node/Python syntax and embedded credential patterns. No publication was made during packaging. Existing Claude Code metadata and command placeholders remain unchanged; each provider must verify its own skill discovery and execution support.

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
