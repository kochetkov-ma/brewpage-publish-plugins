# BrewPage for Qwen Code

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

The 1.1.2 release packages the BrewPage publishing skill for Qwen Code’s extension loader and pins `brewpage-mcp@3.0.0`. The default installation uses the published MCP package.

In the published history, version `1.0.8` moved the pinned MCP server to `2.1.0`, whose guide tool also explains the ready page templates. The publishing skill stays at upstream `5da825f1`; the User-Agent is `brewpage-qwen/1.0.8 (+https://brewpage.app)`. Version `1.0.7` moved the pinned MCP server to `2.0.0`: one tool per job (`publish_html` publishes a page or a whole site, `get_page` reads, `set_publication` changes the settings), and the older tool names still answer. Version `1.0.6` synced the publishing skill to upstream `5da825f1` (claude-brewcode v6.12.12), which explains page data: published pages can save what visitors enter, and the author turns it on and reads the entries in the management link's Data tab. It moved the pinned MCP server to `1.19.0`, which added the page data tools. Version `1.0.5` synced the skill to upstream `48255159` (claude-brewcode v6.12.11): after publishing the agent gives you the page link and the management link; the management link is private: anyone who has it can edit or delete the page. The owner token stays in the native history file and is shown when you ask or when it cannot be saved. `.html` and Markdown files publish as pages. Version `1.0.4` added links back to this collection and BrewPage in this guide. Version `1.0.3` synced the publishing skill to upstream `809e0fa2`, so every brewpage.app request sends a User-Agent. `verify-isolation.py` asserts that header on the mocked upload. Launcher bytes are unchanged. Version 1.0.2 updated the pinned MCP server to 1.15.1. Distribute `brewpage-qwen-1.0.8.zip`; `manifest.json` records its inventory and SHA-256. Prior archives and verification receipts remain historical evidence. Manifest keywords do not prove vendor-catalog indexing.

The eleven upstream files under `skills/brewpage-publish/upstream/` come from the MIT-licensed [source commit](https://github.com/kochetkov-ma/claude-brewcode/tree/94e3d609e3308be34c0696276a20331fb65c26f4/skills/brewpage-publish) with User-Agent `brewpage-qwen/1.1.2 (+https://brewpage.app)`. The host uses a compatible BrewPage MCP operation when the selected authority and private result channel are verified. Its isolated runner handles permitted HTTPS fallback and local file intake.

The adapter resolves input and password-file paths before changing directory, removes inherited Claude variables, and forces history into `~/.qwen/brewpage-publish/.claude/brewpage-history.md` (file 600, private state directory 700). The nested filename belongs solely to this adapter's native state. It never imports a project's or another runtime's Claude history or credentials. Never invoke the upstream helper directly.

The helper receives only PATH, HOME and locale variables plus adapter-owned root, private temporary storage and isolated Git settings. Shell startup/options, exported functions and inherited Git context are excluded. Probe, content and password paths containing `.claude` or `.claude-*` components are refused before helper reads, including alternate case and neutral aliases resolving there.

Run `python3 verify-isolation.py --recipes` in the 1.1.2 package to check archive consent, path handling, isolated storage and private recovery with synthetic transport.

## Install

With Node.js `24.19.0` and Qwen Code `0.26.1`, install this extracted directory:

```sh
qwen extensions install /absolute/path/to/qwen
qwen extensions list
qwen mcp list
```

Review and accept Qwen's installation prompt. It must list both the `brewpage-publish` skill and `brewpage` MCP server. The extension list must report `Origin: AgentPlugins`, `brewpage (1.1.2)`, and both capabilities. After public distribution, use the same command on the downloaded and extracted package.

Start Qwen Code, complete its own supported login, and ask it to load `brewpage-publish`. Publishing needs Bash, curl, jq, Python 3 with `fcntl`, and Git inside repositories; sites also need Node, zip and unzip. Use macOS, Linux or WSL. Answer namespace and password choices explicitly. No BrewPage signup or API key is needed.

## Verification

Version 1.0.0 was verified with official Qwen Code `0.26.1`, installed at an exact npm pin into a temporary directory with a separate empty `HOME`. The native loader enumerated `brewpage-publish` and `brewpage`, and `qwen mcp list` established the MCP stdio connection. All seven vendored upstream files matched the common-package SHA256 values. The helper's local `probe` succeeded without publishing. The original receipt is retained as `verification-1.0.0.json`.

`verification.json` records historical 1.0.1 metadata checks. The [1.0.2 refresh receipt](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/download/v1.0.2/qwen-refresh-verification-1.0.2.json) records local archive, pin and unchanged skill/launcher checks; `refresh-verification-1.0.3.json` records the 1.0.3 sync checks, `refresh-verification-1.0.4.json` the 1.0.4 checks, `refresh-verification-1.0.5.json` the 1.0.5 checks, `refresh-verification-1.0.6.json` the 1.0.6 checks, `refresh-verification-1.0.7.json` the 1.0.7 checks and `refresh-verification-1.0.8.json` the 1.0.8 checks. Native installation, MCP connection and isolation fixtures were not repeated for 1.0.2.

No existing client configuration, authentication, API key, model call or BrewPage content upload was used. Skill discovery and MCP connection are verified; model-driven skill execution and rendering of a published result remain unverified.

Native contracts: [Qwen Agent Plugins v1](https://qwenlm.github.io/qwen-code-docs/en/users/extension/agent-plugins/), [manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), [MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json).

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
