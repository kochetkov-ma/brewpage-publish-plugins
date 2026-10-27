# BrewPage publishing skill for Yandex AI Studio

Import `yandex-brewpage-publish-v1.0.1.zip` through Agent Core → Skills → Create skill. It contains one top-level `brewpage-publish/` folder and exactly one active `SKILL.md`. The active Russian description covers HTML hosting, static sites and AI artifact publishing first, then Markdown, documents, reports, JSON and any files shared by link.

The portable instructions use connected BrewPage MCP capabilities and their current schemas. They retain explicit visibility/password choices, preview, TTL, archive review, credential privacy and failure handling. They do not execute the original Claude helpers. Connect the external endpoint `https://brewpage.app/mcp` using Streamable HTTP without authorization; no account or API key is required by BrewPage.

The seven MIT-licensed upstream files come from [the immutable source commit](https://github.com/kochetkov-ma/claude-brewcode/tree/d2d42282fecec988447f9c9547959b31a8012644/skills/brewpage-publish). Their bytes remain unchanged under `upstream/`. The original manifest is named `upstream/SKILL.md.source` to meet Yandex's exactly-one-`SKILL.md` requirement. It is provenance, not the active instruction path. `manifest.json` maps original names and hashes.

The archived bytes match the eight-file package successfully imported into a personal Yandex AI Studio catalog. Native MCP discovery found and saved 20 tools. No model, shell container, agent run, publishing action or public marketplace submission was performed. A stored skill and MCP connection do not prove runtime publishing.

[Skills have no separate fee](https://aistudio.yandex.ru/ru/docs/ai-studio/concepts/agents/skills); content consumed by a model is billed as model context. [MCP-server storage is not billed](https://aistudio.yandex.ru/ru/docs/ai-studio/pricing), while underlying tool services may charge. This package does not provision Cloud Functions, networks, service accounts or paid runtime resources.

Validation covers archive CRC, extracted-file hashes, one active manifest, all seven upstream hashes and portable-body preservation. Historical original-only archives remain available under `../common/` unchanged.
