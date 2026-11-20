# BrewPage for DeepSeek Harness

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

The 1.1.2 release packages the BrewPage publishing skill for DeepSeek Harness and pins `brewpage-mcp@3.0.0`. The default installation uses the published MCP package.

In the published history, version `1.0.8` moved the pinned MCP server to `2.1.0`, whose guide tool also explains the ready page templates. The publishing skill stays at upstream `5da825f1`; the User-Agent is `brewpage-deepseek/1.0.8 (+https://brewpage.app)`. Version `1.0.7` moved the pinned MCP server to `2.0.0`: one tool per job (`publish_html` publishes a page or a whole site, `get_page` reads, `set_publication` changes the settings), and the older tool names still answer. Version `1.0.6` synced the publishing skill to upstream `5da825f1` (claude-brewcode v6.12.12), which explains page data: published pages can save what visitors enter, and the author turns it on and reads the entries in the management link's Data tab. It moved the pinned MCP server to `1.19.0`, which added the page data tools. Version `1.0.5` synced the skill to upstream `48255159` (claude-brewcode v6.12.11): after publishing the agent gives you the page link and the management link; the management link is private: anyone who has it can edit or delete the page. The owner token stays in the native history file and is shown when you ask or when it cannot be saved. `.html` and Markdown files publish as pages. Version `1.0.4` added links back to this collection and BrewPage in this guide. Version `1.0.3` synced the publishing skill to upstream `809e0fa2`, so every brewpage.app request sends a User-Agent. `verify-isolation.py` asserts that header on the mocked upload. Launcher bytes are unchanged. Version `1.0.2` updated the pinned MCP server to `1.15.1`. Earlier release tarballs and verification receipts are retained. Description and keywords become npm search metadata only if published to npm; no npm publication, indexing or Harness catalog ranking is claimed.

The eleven upstream files under `skills/brewpage-publish/upstream/` come from the MIT-licensed [source commit](https://github.com/kochetkov-ma/claude-brewcode/tree/94e3d609e3308be34c0696276a20331fb65c26f4/skills/brewpage-publish) with User-Agent `brewpage-deepseek/1.1.2 (+https://brewpage.app)`. The host uses a compatible BrewPage MCP operation when the selected authority and private result channel are verified. Its isolated runner handles permitted HTTPS fallback and local file intake.

The adapter resolves input and password-file paths before changing directory, removes inherited Claude variables, and forces history into `~/.dsh/brewpage-publish/.claude/brewpage-history.md` (file 600, private state directory 700). The nested filename belongs solely to this adapter's native state. It never imports a project's or another runtime's Claude history or credentials. Never invoke the upstream helper directly.

The helper receives only PATH, HOME and locale variables plus adapter-owned root, private temporary storage and isolated Git settings. Shell startup/options, exported functions and inherited Git context are excluded. Probe, content and password paths containing `.claude` or `.claude-*` components are refused before helper reads, including alternate case and neutral aliases resolving there.

Run `python3 verify-isolation.py --recipes` in the 1.1.2 package to check archive consent, path handling, isolated storage and private recovery with synthetic transport.

## Install

Requires Node.js 24 (verified with `24.19.0` for 1.0.0 and `24.15.0` for 1.0.5 to 1.0.8), pnpm `12.15.0`, and DeepSeek Harness `0.2.1-rc.2`. From this extracted directory:

```sh
npm pack --ignore-scripts
dsh plugin --profile brewpage add ./dsh-brewpage-1.1.2.tgz
dsh --profile brewpage --dump-config
```

Install the tarball rather than this hub's private Git repository. A public download URL may replace the local tarball only after publication. The bundle uses the installed Harness's native skill provider and MCP client; no build script, API key or copied authentication is needed. Publishing needs the upstream POSIX helper prerequisites: Bash, curl, jq, Python 3 with `fcntl`, and Git inside repositories; sites also need Node, zip and unzip. Native Windows requires WSL.

Boot a profile with a configured model and ask it to load `brewpage-publish`. Answer namespace and password choices explicitly. Full model execution requires that profile's own provider login/configuration; a logged-in browser session at DeepSeek's consumer website does not configure Harness.

## Verification

Verified with Node `24.19.0` and Harness `0.2.1-rc.2` in a fresh temporary `DSH_HOME`: official `dsh plugin add`, composed `--dump-config`, and `--dump-config-schema` succeeded. The native Cordis context, actual skill registry and actual filesystem provider discovered exactly `brewpage-publish` and loaded its body, with both invocation policies enabled. The source files matched all seven common-package SHA256 values. The helper's local `probe` succeeded without publishing.

To repeat the native fixture, create an isolated temporary directory, copy `verify-native.mjs` there, then run:

```sh
npm install --ignore-scripts --no-audit --no-fund @deepseek-ai/dsh@0.2.1-rc.2 /absolute/path/dsh-brewpage-1.1.2.tgz
node verify-native.mjs
```

No model call, API key, content upload or existing-client installation was used. Model-driven execution and rendering of a published result remain unverified. Default Node `20.15.0` silently skipped the Harness CLI's `import.meta.main` entry point; use the verified Node version.

Native verification above records the `1.0.0` baseline; `metadata-verification.json` records historical `1.0.1` checks. The [1.0.2 refresh receipt](https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/download/v1.0.2/deepseek-refresh-verification-1.0.2.json) records local archive, pin and unchanged skill/launcher checks; `refresh-verification-1.0.3.json` records the 1.0.3 sync checks, `refresh-verification-1.0.4.json` the 1.0.4 checks, `refresh-verification-1.0.5.json` the 1.0.5 checks, `refresh-verification-1.0.6.json` the 1.0.6 checks, `refresh-verification-1.0.7.json` the 1.0.7 checks and `refresh-verification-1.0.8.json` the 1.0.8 checks (the latter three including the native fixture above with Node `24.15.0`). Native installation, MCP connection and isolation fixtures were not repeated for `1.0.2`.

Native contracts: [bundle packaging](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish.html), [skill provider](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/skill/skill-filesystem), [MCP bundle template](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/preset/agent-preset/skills/cordis-plugin-development/templates/mcp).

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
