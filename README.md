# BrewPage publishing plugins

Host HTML pages and static sites, publish AI artifacts, and share Markdown, documents, reports or any file by link with [BrewPage](https://brewpage.app). These MIT-licensed publishing skills and native adapters preserve explicit publication choices and keep ownership credentials private.

## Download and install

Download the matching artifact from [release v1.0.1](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/tag/v1.0.1), review its contents, verify its [SHA-256](SHASUMS256.txt), and follow the package guide:

| Host | Artifact | Installation guide |
|---|---|---|
| Qwen Code | `brewpage-qwen-1.0.1.zip` | [Qwen](qwen/README.md) |
| DeepSeek Harness | `dsh-brewpage-1.0.1.tgz` | [DeepSeek](deepseek/README.md) |
| Mistral Vibe Code | `brewpage-vibe-1.0.1.zip` | [Vibe Code](mistral/brewpage/README.md) |
| Kimi Code | `brewpage-kimi-code-1.0.1.zip` | [Kimi Code](kimi/README.md) |
| Skill directory / ZIP | `brewpage-publish.zip` (unchanged original) | [Original skill](common/README.md) |
| Yandex AI Studio | `yandex-brewpage-publish-v1.0.1.zip` | [Portable MCP adapter](yandex/README.md) |
| Mistral Work | `mistral-work-brewpage-publish-v1.0.1.zip` | [MCP skill adapter](common/mistral-work/SKILL.md) |

For source installation, use this release tag:

```sh
git clone --branch v1.0.1 --depth 1 https://github.com/kochetkov-ma/brewpage-publish-plugins.git
```

The package guides contain installation commands and pinned host versions. BrewPage needs no signup or API key; a host may require its own login or provider configuration. Review visibility, password and expiry choices before publishing. Keep ownership credentials out of shared output.

Version 1.0.1 updates discovery descriptions for HTML hosting, static sites and AI artifact publishing, followed by Markdown, documents, reports and any files. It also adds the portable Yandex adapter source. Historical assets remain available unchanged in [release v1.0.0](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/tag/v1.0.0).

## Provenance and limits

All seven original skill files retain their MIT license and immutable [claude-brewcode source](https://github.com/kochetkov-ma/claude-brewcode/tree/d2d42282fecec988447f9c9547959b31a8012644/skills/brewpage-publish). [PROVENANCE.json](PROVENANCE.json) lists the exact distribution-source and release-asset hashes. Yandex preserves the original manifest as `upstream/SKILL.md.source` so its archive contains exactly one active `SKILL.md`.

These are independent GitHub distributions. Publication here does not establish admission to an official vendor catalog. The Yandex package was imported into a personal AI Studio catalog and its MCP tools discovered; runtime publishing and public marketplace submission are unverified. Import and execution of the exact Mistral Work ZIP remain unverified. Native package verification records distinguish the 1.0.0 installation baseline from the 1.0.1 metadata and archive checks. Model-driven publishing and resulting hosted-page rendering have not been verified.

MIT; see [LICENSE](LICENSE). The license covers these distributed files, not the hosted BrewPage service or vendor products.
