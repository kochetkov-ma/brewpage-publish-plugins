# BrewPage for DeepSeek Harness

Native Harness bundle containing the existing BrewPage publishing skill and the pinned `brewpage-mcp@1.14.4` stdio server. This is for DeepSeek Harness, not the DeepSeek consumer chat website or a consumer plugin store.

Version `1.0.1` updates discovery metadata: host HTML pages and static sites, publish AI artifacts, and share Markdown, documents, reports or any file. Runtime, security and immutable source remain unchanged. The exact `1.0.0` release tarball is retained alongside the new tarball. Description and keywords become npm search metadata only if published to npm; no npm publication, indexing or Harness catalog ranking is claimed.

The seven upstream files under `skills/brewpage-publish/upstream/` are unchanged from the MIT-licensed [source commit](https://github.com/kochetkov-ma/claude-brewcode/tree/d2d42282fecec988447f9c9547959b31a8012644/skills/brewpage-publish). The native skill translates Claude tools and uses `scripts/brewpage-native.py` for every helper invocation. It preserves explicit consent, archive review and token secrecy; MCP accompanies the existing workflow.

The adapter resolves input and password-file paths before changing directory, removes inherited Claude variables, and forces history into `~/.dsh/brewpage-publish/.claude/brewpage-history.md` (file 600, private state directory 700). The nested filename belongs solely to this adapter's native state. It never imports a project's or another runtime's Claude history or credentials. Never invoke the upstream helper directly.

The helper receives only PATH, HOME and locale variables plus adapter-owned root, private temporary storage and isolated Git settings. Shell startup/options, exported functions and inherited Git context are excluded. Probe, content and password paths containing `.claude` or `.claude-*` components are refused before helper reads, including alternate case and neutral aliases resolving there.

Run `python3 verify-isolation.py` to repeat the isolated canary fixture. It exercises actual helper response handling with mocked curl, inherited BASH_ENV/SHELLOPTS/Git attacks, fourteen forbidden path cases and valid relative input/password paths. On macOS it asserts actual case-insensitive access before alternate-case regressions. It verifies unchanged foreign/native history on rejection, native-only owner storage, 700/600 permissions, archive consent and no owner token output. It makes no network request.

## Install

Requires Node.js `24.19.0`, pnpm `12.15.0`, and DeepSeek Harness `0.2.1-rc.2`. From this extracted directory:

```sh
npm pack --ignore-scripts
dsh plugin --profile brewpage add ./dsh-brewpage-1.0.1.tgz
dsh --profile brewpage --dump-config
```

Install the tarball rather than this hub's private Git repository. A public download URL may replace the local tarball only after publication. The bundle uses the installed Harness's native skill provider and MCP client; no build script, API key or copied authentication is needed. Publishing needs the upstream POSIX helper prerequisites: Bash, curl, jq, Python 3 with `fcntl`, and Git inside repositories; sites also need Node, zip and unzip. Native Windows requires WSL.

Boot a profile with a configured model and ask it to load `brewpage-publish`. Answer namespace and password choices explicitly. Full model execution requires that profile's own provider login/configuration; a logged-in browser session at DeepSeek's consumer website does not configure Harness.

## Verification

Verified with Node `24.19.0` and Harness `0.2.1-rc.2` in a fresh temporary `DSH_HOME`: official `dsh plugin add`, composed `--dump-config`, and `--dump-config-schema` succeeded. The native Cordis context, actual skill registry and actual filesystem provider discovered exactly `brewpage-publish` and loaded its body, with both invocation policies enabled. The source files matched all seven common-package SHA256 values. The helper's local `probe` succeeded without publishing.

To repeat the native fixture, create an isolated temporary directory, copy `verify-native.mjs` there, then run:

```sh
npm install --ignore-scripts --no-audit --no-fund @deepseek-ai/dsh@0.2.1-rc.2 /absolute/path/dsh-brewpage-1.0.1.tgz
node verify-native.mjs
```

No model call, API key, content upload or existing-client installation was used. Model-driven execution and rendering of a published result remain unverified. Default Node `20.15.0` silently skipped the Harness CLI's `import.meta.main` entry point; use the verified Node version.

Native verification above records the `1.0.0` baseline. For `1.0.1`, `metadata-verification.json` records package metadata, archive roundtrip, unchanged runtime/security bytes and all seven source hashes; it does not claim a repeated native install or model execution.

Native contracts: [bundle packaging](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish.html), [skill provider](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/skill/skill-filesystem), [MCP bundle template](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/preset/agent-preset/skills/cordis-plugin-development/templates/mcp).
