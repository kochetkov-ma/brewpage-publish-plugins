# BrewPage publishing skill for Yandex AI Studio

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

Import [yandex-brewpage-publish-v1.1.0.zip](yandex-brewpage-publish-v1.1.0.zip) through Agent Core → Skills → Create skill. Its twelve files share one top-level `brewpage-publish/` folder and one active [SKILL.md](brewpage-publish/SKILL.md). The Russian description covers HTML hosting, static sites, AI artifacts, Markdown, documents, reports, JSON and files shared by link.

For anonymous publishing, connect `https://brewpage.app/mcp` using Streamable HTTP. The skill uses the connected BrewPage MCP tools and their schemas exclusively. It leaves unavailable operations pending and retains explicit visibility and password choices, preview, TTL, archive review and failure handling.

A write that can issue a private management link or owner key requires verified owner-only delivery or a protected handoff. Before creating a new publication that can issue a key, the skill arranges private storage or owner-only delivery. It returns the reader link, expiry and relevant notices after success. Anyone with the private management link can edit or delete the page. The skill confirms saved proof through private readback and reconciles an uncertain result before another write.

The eleven MIT-licensed upstream files, including four recipes, come from [claude-brewcode v6.13.0 at `dd0bd63bc983fcb6c1c36f9ea3603eb014b9c97c`](https://github.com/kochetkov-ma/claude-brewcode/tree/dd0bd63bc983fcb6c1c36f9ea3603eb014b9c97c/skills/brewpage-publish). The package renames the original manifest to `upstream/SKILL.md.source` and substitutes the bundled User-Agent `brewpage-yandex/1.1.0 (+https://brewpage.app)`. [manifest.json](manifest.json) maps the imported names and hashes.

The 1.1.0 verification covers archive integrity, the twelve-file roundtrip, one active manifest and eleven upstream file hashes. Fresh native import, model-driven publishing and marketplace acceptance remain unverified. See Yandex's [skill documentation](https://aistudio.yandex.ru/ru/docs/ai-studio/concepts/agents/skills) and [pricing](https://aistudio.yandex.ru/ru/docs/ai-studio/pricing) for service and model costs.

## Historical packages and checks

The eight-file 1.0.1 archive was imported into one personal Yandex AI Studio catalog. Native discovery found and saved twenty tools at that time. Version 1.0.3 updated the receipt instructions, and 1.0.4 through 1.0.6 kept that portable instruction body. Releases 1.0.1 through 1.0.6 are listed in the manifest. The earlier original-only archive remains in [common/](../common/README.md).

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
