# BrewPage for Qwen Code

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

Agent Plugins v1 package containing the existing BrewPage publishing skill and pinned `brewpage-mcp@1.19.0` stdio server. This targets Qwen Code's native extension loader, not Qwen consumer chat or a consumer plugin store.

Version `1.0.6` syncs the publishing skill to upstream `5da825f1` (claude-brewcode v6.12.12), which explains page data: published pages can save what visitors enter, and the author turns it on and reads the entries in the management link's Data tab. It moves the pinned MCP server to `1.19.0`, which adds the page data tools, and sets the User-Agent to `brewpage-qwen/1.0.6 (+https://brewpage.app)`. Version `1.0.5` synced the skill to upstream `48255159` (claude-brewcode v6.12.11): after publishing the agent gives you the page link and the management link; the management link is private: anyone who has it can edit or delete the page. The owner token stays in the native history file and is shown when you ask or when it cannot be saved. `.html` and Markdown files publish as pages. Version `1.0.4` added links back to this collection and BrewPage in this guide. Version `1.0.3` synced the publishing skill to upstream `809e0fa2`, so every brewpage.app request sends a User-Agent. `verify-isolation.py` asserts that header on the mocked upload. Launcher bytes are unchanged. Version 1.0.2 updated the pinned MCP server to 1.15.1. Distribute `brewpage-qwen-1.0.6.zip`; `manifest.json` records its inventory and SHA-256. Prior archives and verification receipts remain historical evidence. Manifest keywords do not prove vendor-catalog indexing.

The seven upstream files under `skills/brewpage-publish/upstream/` are synced from the MIT-licensed [source commit](https://github.com/kochetkov-ma/claude-brewcode/tree/5da825f1d535d9658f0de0893529c6ce06a613a5/skills/brewpage-publish); the only deviation is the User-Agent value `brewpage-qwen/1.0.6 (+https://brewpage.app)` (the `BP_UA` line, the delete hint and the README/SKILL curl examples). The native skill translates Claude tools and uses `scripts/brewpage-native.py` for every helper invocation. It preserves explicit consent, archive review and private owner-token history; MCP accompanies the existing workflow.

The adapter resolves input and password-file paths before changing directory, removes inherited Claude variables, and forces history into `~/.qwen/brewpage-publish/.claude/brewpage-history.md` (file 600, private state directory 700). The nested filename belongs solely to this adapter's native state. It never imports a project's or another runtime's Claude history or credentials. Never invoke the upstream helper directly.

The helper receives only PATH, HOME and locale variables plus adapter-owned root, private temporary storage and isolated Git settings. Shell startup/options, exported functions and inherited Git context are excluded. Probe, content and password paths containing `.claude` or `.claude-*` components are refused before helper reads, including alternate case and neutral aliases resolving there.

Run `python3 verify-isolation.py` to repeat the isolated canary fixture. It exercises actual helper response handling with mocked curl, inherited BASH_ENV/SHELLOPTS/Git attacks, fourteen forbidden path cases and valid relative input/password paths. On macOS it asserts actual case-insensitive access before alternate-case regressions. It verifies unchanged foreign/native history on rejection, native-only owner storage, 700/600 permissions, archive consent, the management link on output and no saved owner token on output; when history cannot keep the token, the link, management link and token are handed over. It makes no network request.

## Install

With Node.js `24.19.0` and Qwen Code `0.26.1`, install this extracted directory:

```sh
qwen extensions install /absolute/path/to/qwen
qwen extensions list
qwen mcp list
```

Review and accept Qwen's installation prompt. It must list both the `brewpage-publish` skill and `brewpage` MCP server. The extension list must report `Origin: AgentPlugins`, `brewpage (1.0.6)`, and both capabilities. After public distribution, install the downloaded/extracted package using the same local-directory command; a private hub repository is not a public install source.

Start Qwen Code, complete its own supported login, and ask it to load `brewpage-publish`. Publishing needs Bash, curl, jq, Python 3 with `fcntl`, and Git inside repositories; sites also need Node, zip and unzip. Use macOS, Linux or WSL. Answer namespace and password choices explicitly. No BrewPage signup or API key is needed.

## Verification

Version 1.0.0 was verified with official Qwen Code `0.26.1`, installed at an exact npm pin into a temporary directory with a separate empty `HOME`. The native loader enumerated `brewpage-publish` and `brewpage`, and `qwen mcp list` established the MCP stdio connection. All seven vendored upstream files matched the common-package SHA256 values. The helper's local `probe` succeeded without publishing. The original receipt is retained as `verification-1.0.0.json`.

`verification.json` records historical 1.0.1 metadata checks. The [1.0.2 refresh receipt](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/download/v1.0.2/qwen-refresh-verification-1.0.2.json) records local archive, pin and unchanged skill/launcher checks; `refresh-verification-1.0.3.json` records the 1.0.3 sync checks, `refresh-verification-1.0.4.json` the 1.0.4 checks, `refresh-verification-1.0.5.json` the 1.0.5 checks and `refresh-verification-1.0.6.json` the 1.0.6 checks. Native installation, MCP connection and isolation fixtures were not repeated for 1.0.2.

No existing client configuration, authentication, API key, model call or BrewPage content upload was used. Skill discovery and MCP connection are verified; model-driven skill execution and rendering of a published result remain unverified.

Native contracts: [Qwen Agent Plugins v1](https://qwenlm.github.io/qwen-code-docs/en/users/extension/agent-plugins/), [manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), [MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json).

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
