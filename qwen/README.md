# BrewPage for Qwen Code

Agent Plugins v1 package containing the existing BrewPage publishing skill and pinned `brewpage-mcp@1.14.4` stdio server. This targets Qwen Code's native extension loader, not Qwen consumer chat or a consumer plugin store.

Version 1.0.1 updates discovery metadata for HTML hosting, static sites and AI artifact publishing, followed by Markdown, documents, reports and any files. Launcher, MCP configuration, consent and security behavior are unchanged. Manifest keywords do not prove vendor-catalog indexing; the active skill description supplies the runtime selection trigger. Distribute `brewpage-qwen-1.0.1.zip`; `manifest.json` records its inventory and SHA-256.

The seven upstream files under `skills/brewpage-publish/upstream/` are unchanged from the MIT-licensed [source commit](https://github.com/kochetkov-ma/claude-brewcode/tree/d2d42282fecec988447f9c9547959b31a8012644/skills/brewpage-publish). The native skill translates Claude tools and uses `scripts/brewpage-native.py` for every helper invocation. It preserves explicit consent, archive review and token secrecy; MCP accompanies the existing workflow.

The adapter resolves input and password-file paths before changing directory, removes inherited Claude variables, and forces history into `~/.qwen/brewpage-publish/.claude/brewpage-history.md` (file 600, private state directory 700). The nested filename belongs solely to this adapter's native state. It never imports a project's or another runtime's Claude history or credentials. Never invoke the upstream helper directly.

The helper receives only PATH, HOME and locale variables plus adapter-owned root, private temporary storage and isolated Git settings. Shell startup/options, exported functions and inherited Git context are excluded. Probe, content and password paths containing `.claude` or `.claude-*` components are refused before helper reads, including alternate case and neutral aliases resolving there.

Run `python3 verify-isolation.py` to repeat the isolated canary fixture. It exercises actual helper response handling with mocked curl, inherited BASH_ENV/SHELLOPTS/Git attacks, fourteen forbidden path cases and valid relative input/password paths. On macOS it asserts actual case-insensitive access before alternate-case regressions. It verifies unchanged foreign/native history on rejection, native-only owner storage, 700/600 permissions, archive consent and no owner token output. It makes no network request.

## Install

With Node.js `24.19.0` and Qwen Code `0.26.1`, install this extracted directory:

```sh
qwen extensions install /absolute/path/to/qwen
qwen extensions list
qwen mcp list
```

Review and accept Qwen's installation prompt. It must list both the `brewpage-publish` skill and `brewpage` MCP server. The extension list must report `Origin: AgentPlugins`, `brewpage (1.0.1)`, and both capabilities. After public distribution, install the downloaded/extracted package using the same local-directory command; a private hub repository is not a public install source.

Start Qwen Code, complete its own supported login, and ask it to load `brewpage-publish`. Publishing needs Bash, curl, jq, Python 3 with `fcntl`, and Git inside repositories; sites also need Node, zip and unzip. Use macOS, Linux or WSL. Answer namespace and password choices explicitly. No BrewPage signup or API key is needed.

## Verification

Version 1.0.0 was verified with official Qwen Code `0.26.1`, installed at an exact npm pin into a temporary directory with a separate empty `HOME`. The native loader enumerated `brewpage-publish` and `brewpage`, and `qwen mcp list` established the MCP stdio connection. All seven vendored upstream files matched the common-package SHA256 values. The helper's local `probe` succeeded without publishing. The original receipt is retained as `verification-1.0.0.json`.

Version 1.0.1 has fresh schema, archive and unchanged-runtime hash checks in `verification.json`; native installation, MCP connection and isolation fixtures were not repeated for this metadata-only update.

No existing client configuration, authentication, API key, model call or BrewPage content upload was used. Skill discovery and MCP connection are verified; model-driven skill execution and rendering of a published result remain unverified.

Native contracts: [Qwen Agent Plugins v1](https://qwenlm.github.io/qwen-code-docs/en/users/extension/agent-plugins/), [manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), [MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json).
