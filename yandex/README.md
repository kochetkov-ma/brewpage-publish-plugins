# BrewPage publishing skill for Yandex AI Studio

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

Import `yandex-brewpage-publish-v1.0.4.zip` through Agent Core → Skills → Create skill. It contains one top-level `brewpage-publish/` folder and exactly one active `SKILL.md`. The active Russian description covers HTML hosting, static sites and AI artifact publishing first, then Markdown, documents, reports, JSON and any files shared by link.

The portable instructions use connected BrewPage MCP capabilities and their current schemas. They retain explicit visibility/password choices, preview, TTL, archive review and failure handling. Since v1.0.3 the agent gives you the reader URL and the management link after publishing; the management link is private: anyone who has it can edit or delete the page. The owner token is kept in private supported storage, or handed to you when there is none; neither is posted publicly. They do not execute the original Claude helpers. Connect the external endpoint `https://brewpage.app/mcp` using Streamable HTTP without authorization; no account or API key is required by BrewPage.

The seven MIT-licensed upstream files come from [the immutable source commit](https://github.com/kochetkov-ma/claude-brewcode/tree/5da825f1d535d9658f0de0893529c6ce06a613a5/skills/brewpage-publish) (v1.0.4, claude-brewcode v6.12.12, which adds the page data note); under `upstream/` they differ only in the User-Agent value `brewpage-yandex/1.0.4 (+https://brewpage.app)`. The active instructions use MCP and never run them. The original manifest is named `upstream/SKILL.md.source` to meet Yandex's exactly-one-`SKILL.md` requirement. It is provenance, not the active instruction path. `manifest.json` maps original names and hashes.

The v1.0.1 archive (retained, as are v1.0.2 and v1.0.3) matches the eight-file package successfully imported into a personal Yandex AI Studio catalog; v1.0.3 and v1.0.4 were not imported again. Native MCP discovery found and saved 20 tools. No model, shell container, agent run, publishing action or public marketplace submission was performed. A stored skill and MCP connection do not prove runtime publishing.

[Skills have no separate fee](https://aistudio.yandex.ru/ru/docs/ai-studio/concepts/agents/skills); content consumed by a model is billed as model context. [MCP-server storage is not billed](https://aistudio.yandex.ru/ru/docs/ai-studio/pricing), while underlying tool services may charge. This package does not provision Cloud Functions, networks, service accounts or paid runtime resources.

Validation covers archive CRC, extracted-file hashes, one active manifest, all seven upstream hashes and the portable body hash (new in v1.0.3: the result rule changed; unchanged in v1.0.4). Historical original-only archives remain available under `../common/` unchanged.

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
