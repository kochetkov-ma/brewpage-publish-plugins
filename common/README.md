# Existing BrewPage publish skill

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

This package preserves all seven MIT-licensed source files from [brewpage-publish at `4825515919e33266eb8f44587f161040a2dac9ae`](https://github.com/kochetkov-ma/claude-brewcode/tree/4825515919e33266eb8f44587f161040a2dac9ae/skills/brewpage-publish) (claude-brewcode v6.12.11), byte for byte.

Use the `brewpage-publish` folder where a provider accepts a skill directory, or upload `brewpage-publish.zip` where it accepts a ZIP. The ZIP opens directly to `SKILL.md`, `README.md`, `LICENSE` and `scripts/`. `manifest.json` records source and artifact hashes.

The historical `yandex-brewpage-publish.zip` preserves the seven original Claude-oriented files in one top-level folder. Use the [portable Yandex adapter](../yandex/README.md) for a connected-MCP workflow: its eight-file archive was imported into a personal AI Studio catalog. Import and tool discovery do not prove model execution or public marketplace acceptance.

For Mistral Work, use `mistral-work-brewpage-publish-v1.0.3.zip`: it syncs `upstream/` to that commit with User-Agent `brewpage-mistral-work/1.0.3 (+https://brewpage.app)` and changes one paragraph of the portable instruction body, the result rule: the agent gives you the reader URL and the management link. v1.0.2 and v1.0.1 are retained. Its root `SKILL.md` describes HTML hosting, static sites and AI artifact publishing, followed by Markdown, documents, reports and any files. The root MIT license and the seven original files under `upstream/` are preserved. The older `mistral-work-brewpage-publish.zip` remains unchanged. The active instructions retain explicit visibility/password choices, preview, TTL and archive consent; native import and execution remain separate checks.

The existing skill requires explicit namespace and password choices before publishing. No account or API key is required. After publishing the agent gives you the page link and the management link; the management link is private: anyone who has it can edit or delete the page. The original Claude workflow keeps the owner token in private local history and shows it when you ask. Portable Work adapters keep the owner token only in evidenced private supported storage and hand it to you otherwise. Neither is posted publicly (public page, repo, shared channel); never paste a password into chat.

Packaging checks cover immutable source hashes, seven-file ZIP roundtrip, shell/Node/Python syntax and embedded credential patterns. No publication was made during packaging. Existing Claude Code metadata and command placeholders remain unchanged; each provider must verify its own skill discovery and execution support.

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
