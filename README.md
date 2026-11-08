# BrewPage publishing plugins

<a href="https://www.npmjs.com/package/n8n-nodes-brewpage"><img height="18" alt="npm n8n-nodes-brewpage" src="https://img.shields.io/npm/v/n8n-nodes-brewpage?label=n8n-nodes-brewpage"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/n8n-community-node-provenance.yml"><img height="18" alt="n8n node CI" src="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/n8n-community-node-provenance.yml/badge.svg"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/zapier-app.yml"><img height="18" alt="Zapier app CI" src="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/zapier-app.yml/badge.svg"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Publish HTML pages, Markdown, files and static sites from AI agents and
automation tools to [BrewPage](https://brewpage.app) and get an HTTPS link back.
No signup or API key. Publications are temporary: 15 days by default, 30 at most
(90 with a free profile).

## Integrations

AI-agent packages are assets of the latest release,
[v1.0.4](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/tag/v1.0.4);
check them against [SHASUMS256.txt](SHASUMS256.txt).
The agent plugin in `agent-plugin/` installs from this repository, which is also its Claude Code and Cursor marketplace.

| Host | Folder | Install or use | Guide |
| --- | --- | --- | --- |
| Claude Code, Grok Build, Cursor, GitHub Copilot | `agent-plugin/` | Claude Code: `/plugin marketplace add kochetkov-ma/brewpage-publish-plugins`, then `/plugin install brewpage@brewpage` | [README](agent-plugin/README.md) |
| Google Antigravity | `integrations/antigravity-plugin/` | `agy plugin install ./integrations/antigravity-plugin` from a clone | [README](integrations/antigravity-plugin/README.md) |
| Qwen Code | `qwen/` | `qwen extensions install /absolute/path/to/qwen` from `brewpage-qwen-1.0.4.zip` | [README](qwen/README.md) |
| DeepSeek Harness | `deepseek/` | `dsh plugin --profile brewpage add ./dsh-brewpage-1.0.4.tgz` | [README](deepseek/README.md) |
| Mistral Vibe Code | `mistral/` | Extract `brewpage-vibe-1.0.2.zip` into `.vibe/plugins/`, then `/reload-plugins` | [README](mistral/README.md) |
| Kimi Code | `kimi/` | Extract `brewpage-kimi-code-1.0.2.zip`, then `/plugins install /absolute/path/to/brewpage-publish` | [README](kimi/README.md) |
| Yandex AI Studio | `yandex/` | Import `yandex-brewpage-publish-v1.0.2.zip` in Agent Core > Skills | [README](yandex/README.md) |
| Mistral Work | `common/` | Use `mistral-work-brewpage-publish-v1.0.2.zip` | [SKILL.md](common/mistral-work/SKILL.md) |
| Any skill directory or ZIP | `common/` | Use the `brewpage-publish/` folder or `brewpage-publish.zip` (original Claude skill) | [README](common/README.md) |
| n8n (self-hosted) | `integrations/n8n-community-node/` | Settings > Community nodes > install `n8n-nodes-brewpage` | [README](integrations/n8n-community-node/package/README.md) |
| n8n workflow template | `integrations/n8n-templates/` | Import `brewpage-release-digest.json` as a workflow; no community node or credentials | [README](integrations/n8n-templates/README.md) |
| AnythingLLM | `integrations/anythingllm-skill/` | Copy into `plugins/agent-skills/brewpage-publish/`; Community Hub listing pending | [README](integrations/anythingllm-skill/README.md) |
| Zapier | `integrations/zapier-app/` | Source of the Zapier integration; App Directory listing pending | [README](integrations/zapier-app/README.md) |

Every package states its pinned host versions, verification records and limits
in its guide. [PROVENANCE.json](PROVENANCE.json) lists the source and release
hashes of the AI-agent packages; the n8n and Zapier integrations have their own
CI workflows under [`.github/workflows`](.github/workflows). These are
independent distributions: a package here does not mean a vendor catalog has
accepted it.

## Related

- [brewpage.app](https://brewpage.app): the hosting service; [API guide](https://brewpage.app/api); [OpenAPI docs](https://kochetkov-ma.github.io/brewpage-openapi/)
- [brewpage-openapi](https://github.com/kochetkov-ma/brewpage-openapi): OpenAPI contract and the `brewpage-mcp` MCP server ([npm](https://www.npmjs.com/package/brewpage-mcp))
- [brewpage-action](https://github.com/kochetkov-ma/brewpage-action): GitHub Action that publishes CI artifacts ([Marketplace](https://github.com/marketplace/actions/publish-to-brewpage))
- [brewpage-cookbook](https://github.com/kochetkov-ma/brewpage-cookbook): interactive recipes published on BrewPage
- [brewpage-obsidian](https://github.com/kochetkov-ma/brewpage-obsidian): Obsidian plugin that publishes notes ([Obsidian community](https://community.obsidian.md/plugins/brewpage-publisher))
- [brewpage-browser-extension](https://github.com/kochetkov-ma/brewpage-browser-extension): browser extension that publishes pages, selections and files
- [brewpage-codex-plugin](https://github.com/kochetkov-ma/brewpage-codex-plugin): Codex plugin with the publishing skill and remote MCP
- [langchain-brewpage](https://github.com/kochetkov-ma/langchain-brewpage): LangChain tools ([PyPI](https://pypi.org/project/langchain-brewpage/))
- [llama-index-tools-brewpage](https://github.com/kochetkov-ma/llama-index-tools-brewpage): LlamaIndex tool spec ([PyPI](https://pypi.org/project/llama-index-tools-brewpage/))

## Support and license

Questions and problems: [info@brewpage.app](mailto:info@brewpage.app).

MIT; see [LICENSE](LICENSE). The license covers the files in this repository,
not the hosted BrewPage service or vendor products.
