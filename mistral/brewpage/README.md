# BrewPage for Mistral Vibe Code

An Agent Plugins 1.0 package containing the existing MIT-licensed BrewPage publishing skill and the remote BrewPage MCP server. No separate prompt, model or publishing runtime is added.

Version 1.0.4 syncs the bundled skill to upstream `5da825f1` (claude-brewcode v6.12.12), which explains page data: published pages can save what visitors enter, and the author turns it on and reads the entries in the management link's Data tab; the runner sends `User-Agent: brewpage-mistral-vibe/1.0.4 (+https://brewpage.app)`. Version 1.0.3 synced it to upstream `48255159` (claude-brewcode v6.12.11): after publishing the agent gives you the page link and the management link; the management link is private: anyone who has it can edit or delete the page. The owner token stays in the isolated history file and is shown when you ask or when it cannot be saved. `.html` and Markdown files publish as pages. Version 1.0.2 synced the bundled skill to upstream `809e0fa2`, so every brewpage.app request sends a User-Agent. Version 1.0.1 updated discovery metadata for HTML hosting, static sites and AI artifact publishing, followed by Markdown, documents, reports and any files. Launcher, MCP configuration and consent behavior are unchanged. Manifest keywords do not prove vendor-catalog indexing; the active skill description supplies the runtime selection trigger.

## Install

Review the files, then extract `brewpage-vibe-1.0.4.zip` into your project's `.vibe/plugins/` directory. The resulting manifest must be `.vibe/plugins/brewpage/plugin.json`. Trust that project in Vibe Code, then start a session or run `/reload-plugins`. Open `/plugins` to inspect BrewPage and `/mcp` to inspect its remote server.

Vibe Code exposes the bundled skill as `/brewpage:brewpage-publish`. The MCP endpoint is `https://brewpage.app/mcp` (Streamable HTTP, no API key or account required). Normal Vibe approval rules apply to MCP tools.

## Existing skill compatibility

All seven original skill files are synced under `skills/brewpage-publish/upstream/` from `skills/brewpage-publish` at commit `5da825f1d535d9658f0de0893529c6ce06a613a5` of [claude-brewcode](https://github.com/kochetkov-ma/claude-brewcode/tree/5da825f1d535d9658f0de0893529c6ce06a613a5/skills/brewpage-publish); the only deviation is the User-Agent value.

The small native `SKILL.md` adapter loads the original workflow and translates its tool names and invocation arguments to Vibe's host tools. Its local `run.py` launcher executes the existing secure runner in a private Mistral workspace; no publishing code is rewritten. Content and password paths must be absolute; Claude configuration/history paths are refused. Vibe's approvals apply.

Owner history is isolated at `$VIBE_HOME/brewpage-publish-state/.claude/brewpage-history.md` (default `~/.vibe/brewpage-publish-state/.claude/brewpage-history.md`), with a 0700 state directory and 0600 history. The launcher discards inherited Claude/Git environment and imports no authentication. Run `python3 '<installed skill directory>/run.py' --check-isolation` to initialize and check this local state without uploading content; it prints only the isolated path.

Native loading, skill exposure and MCP tool discovery were checked on version 1.0.0 without publishing content or calling a model. Versions 1.0.1 to 1.0.4 have fresh schema, archive and launcher hash checks; native loading and MCP discovery were not repeated. An end-to-end model-driven publishing run has not been performed. The remote MCP tools are independently available; the skill uses the runner to retain its archive-review and token-history safeguards.

## License and verification

The package and bundled skill use MIT; see `LICENSE`. The companion distribution files `manifest.json` and `validation.json` record artifact hashes, the exact vendor version and checks performed, including their limits.

The package follows [Mistral's plugin documentation](https://docs.mistral.ai/vibe/code/cli/plugins). Plugin support is experimental. This CLI package is separate from any connector configured in Le Chat.
