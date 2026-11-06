# BrewPage publishing plugins

[![License: MIT](https://img.shields.io/github/license/kochetkov-ma/brewpage-publish-plugins)](LICENSE)
[![npm n8n-nodes-brewpage](https://img.shields.io/npm/v/n8n-nodes-brewpage?label=n8n-nodes-brewpage)](https://www.npmjs.com/package/n8n-nodes-brewpage)
[![npm brewpage-mcp](https://img.shields.io/npm/v/brewpage-mcp?label=brewpage-mcp)](https://www.npmjs.com/package/brewpage-mcp)

Publish HTML pages, Markdown, files and static sites from AI agents and
automation tools to [BrewPage](https://brewpage.app) and get an HTTPS link back.
No signup or API key. Publications are temporary: 15 days by default, 30 at most
(90 with a free profile).

## Integrations

AI-agent packages are assets of the latest release,
[v1.0.3](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/tag/v1.0.3);
check them against [SHASUMS256.txt](SHASUMS256.txt).

| Host | Folder | Install or use | Guide |
| --- | --- | --- | --- |
| Qwen Code | `qwen/` | `qwen extensions install /absolute/path/to/qwen` from `brewpage-qwen-1.0.3.zip` | [README](qwen/README.md) |
| DeepSeek Harness | `deepseek/` | `dsh plugin --profile brewpage add ./dsh-brewpage-1.0.3.tgz` | [README](deepseek/README.md) |
| Mistral Vibe Code | `mistral/` | Extract `brewpage-vibe-1.0.2.zip` into `.vibe/plugins/`, then `/reload-plugins` | [README](mistral/brewpage/README.md) |
| Kimi Code | `kimi/` | Extract `brewpage-kimi-code-1.0.2.zip`, then `/plugins install /absolute/path/to/brewpage-publish` | [README](kimi/README.md) |
| Yandex AI Studio | `yandex/` | Import `yandex-brewpage-publish-v1.0.2.zip` in Agent Core > Skills | [README](yandex/README.md) |
| Mistral Work | `common/` | Use `mistral-work-brewpage-publish-v1.0.2.zip` | [SKILL.md](common/mistral-work/SKILL.md) |
| Any skill directory or ZIP | `common/` | Use the `brewpage-publish/` folder or `brewpage-publish.zip` (original Claude skill) | [README](common/README.md) |
| n8n (self-hosted) | `integrations/n8n-community-node/` | Settings > Community nodes > install `n8n-nodes-brewpage` | [README](integrations/n8n-community-node/package/README.md) |
| Zapier | `integrations/zapier-app/` | Source of the Zapier integration; App Directory listing pending | [README](integrations/zapier-app/README.md) |

Every package states its pinned host versions, verification records and limits
in its guide. [PROVENANCE.json](PROVENANCE.json) lists the source and release
hashes of the AI-agent packages; the n8n and Zapier integrations have their own
CI workflows under [`.github/workflows`](.github/workflows). These are
independent distributions: a package here does not mean a vendor catalog has
accepted it.

## Related

- [BrewPage](https://brewpage.app): the hosting service.
- [API guide](https://brewpage.app/api) and the
  [OpenAPI docs site](https://kochetkov-ma.github.io/brewpage-openapi/).
- [MCP server and OpenAPI spec](https://github.com/kochetkov-ma/brewpage-openapi),
  npm [`brewpage-mcp`](https://www.npmjs.com/package/brewpage-mcp); remote
  endpoint `https://brewpage.app/mcp`.
- [GitHub Action "Publish to BrewPage"](https://github.com/marketplace/actions/publish-to-brewpage).
- [Cookbook](https://github.com/kochetkov-ma/brewpage-cookbook): recipes and
  examples.
- LangChain: [`langchain-brewpage`](https://pypi.org/project/langchain-brewpage/)
  ([repo](https://github.com/kochetkov-ma/langchain-brewpage)).
- LlamaIndex:
  [`llama-index-tools-brewpage`](https://pypi.org/project/llama-index-tools-brewpage/)
  ([repo](https://github.com/kochetkov-ma/llama-index-tools-brewpage)).
- n8n: [`n8n-nodes-brewpage`](https://www.npmjs.com/package/n8n-nodes-brewpage).

## Support and license

Questions and problems: [info@brewpage.app](mailto:info@brewpage.app).

MIT; see [LICENSE](LICENSE). The license covers the files in this repository,
not the hosted BrewPage service or vendor products.
