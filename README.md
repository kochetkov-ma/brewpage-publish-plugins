# BrewPage publishing plugins

The existing MIT-licensed BrewPage publishing skill, packaged for Qwen Code, DeepSeek Harness, Mistral Vibe Code and Kimi Code. Packages preserve explicit publication choices; each native adapter documents its owner-capability handling and verification limits.

## Download and install

Download the matching artifact from [release v1.0.0](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/tag/v1.0.0), review its contents, and follow the package guide:

| Host | Artifact | Installation guide |
|---|---|---|
| Qwen Code | `qwen-brewpage-1.0.0.zip` | [Qwen](qwen/README.md) |
| DeepSeek Harness | `dsh-brewpage-1.0.0.tgz` | [DeepSeek](deepseek/README.md) |
| Mistral Vibe Code | `brewpage-vibe-1.0.0.zip` | [Vibe Code](mistral/brewpage/README.md) |
| Kimi Code | `brewpage-kimi-code-1.0.0.zip` | [Kimi Code](kimi/README.md) |
| Skill directory / ZIP | `brewpage-publish.zip` | [Original skill](common/README.md) |
| Yandex AI Studio | `yandex-brewpage-publish.zip` | [Packaging guide](common/README.md) |
| Mistral Work | `mistral-work-brewpage-publish.zip` | [MCP skill adapter](common/mistral-work/SKILL.md) |

For source installation, use this release tag:

```sh
git clone --branch v1.0.0 --depth 1 https://github.com/kochetkov-ma/brewpage-publish-plugins.git
```

The package guides contain the verified native installation commands and pinned host versions. BrewPage needs no signup or API key; a host may require its own login or provider configuration. Review namespace, password and expiry choices before publishing. Keep ownership credentials out of shared output.

## Provenance and limits

All seven original skill files retain their MIT license and immutable [claude-brewcode source](https://github.com/kochetkov-ma/claude-brewcode/tree/d2d42282fecec988447f9c9547959b31a8012644/skills/brewpage-publish). [PROVENANCE.json](PROVENANCE.json) lists the exact distribution-source hashes. Native package receipts describe discovery, connection and isolation checks and their limits.

These are independent GitHub distributions. Publication here does not establish admission to an official vendor catalog. Model-driven publishing and resulting hosted-page rendering have not been verified. Work and Yandex packaging does not establish native import or execution.

MIT; see [LICENSE](LICENSE). The license covers these distributed files, not the hosted BrewPage service or vendor products.
