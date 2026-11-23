# Existing BrewPage publish skill

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

The 1.1.5 distribution preserves all eleven MIT-licensed files from [brewpage-publish at `66ea30dde0553a5984be446ffc9b59b28f2b9505`](https://github.com/kochetkov-ma/claude-brewcode/tree/66ea30dde0553a5984be446ffc9b59b28f2b9505/skills/brewpage-publish) (claude-brewcode v6.13.8), byte for byte.

Use the `brewpage-publish` folder where a provider accepts a skill directory, or upload [brewpage-publish.zip](brewpage-publish.zip) where it accepts a ZIP. The ZIP opens directly to `SKILL.md`, `README.md`, `LICENSE`, `scripts/` and `references/`. The four recipes cover publishing, Page data, custom domains and ownership. [manifest.json](manifest.json) records source and artifact hashes.

The generic skill prefers a compatible BrewPage MCP tool with the selected owner and protected delivery of any private result. It can use authorized REST with the same owner if required and selected before writing. An MCP-only request stays pending if the connected tool cannot perform it. Drafts stay local. If a write outcome is uncertain, check the selected owner's receipt or inventory before another write. The [bundled guide](brewpage-publish/README.md) describes the routes and recovery steps.

## Mistral Work

Use [mistral-work-brewpage-publish-v1.1.5.zip](mistral-work-brewpage-publish-v1.1.5.zip). The thirteen files include a root `LICENSE`, the active [SKILL.md](mistral-work/SKILL.md) and eleven files under `upstream/` with the bundled User-Agent `brewpage-mistral-work/1.1.5 (+https://brewpage.app)`. The active skill uses connected BrewPage MCP only and leaves unsupported operations pending. It keeps explicit visibility and password choices, preview, TTL and archive review.

The skill returns the reader link and delivers any private management link or owner key through a verified owner-only channel. Anyone with the management link can edit or delete the publication. Arrange private storage or protected delivery before a write that can issue a key. The skill confirms storage through private readback.

Packaging verified immutable source hashes, the eleven-file generic and thirteen-file Work ZIP roundtrips, shell, Node.js and Python syntax, and embedded credential patterns. Fresh native Work import and publishing remain unverified.

## Historical packages

Work releases 1.0.1 through 1.0.6 and the original `mistral-work-brewpage-publish.zip` remain available. Work 1.0.3 changed the result rule to return the reader and management links. Work 1.0.5 and 1.0.6 kept the preceding portable instruction body and changed the version.

The historical `yandex-brewpage-publish.zip` preserves seven Claude-oriented files in one top-level folder. For connected MCP, use the [current Yandex adapter](../yandex/README.md). A previous eight-file Yandex adapter was imported into a personal AI Studio catalog.

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
