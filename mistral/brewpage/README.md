# BrewPage for Mistral Vibe Code

An Agent Plugins 1.0 package containing the MIT-licensed BrewPage publishing skill and a connection to the remote BrewPage MCP server.

Version 1.1.0 bundles the publishing workflow and four recipes for publishing, Page data, custom domains and ownership.

## Install

Review the files, then extract `brewpage-vibe-1.1.0.zip` into your project's `.vibe/plugins/` directory. The resulting manifest must be `.vibe/plugins/brewpage/plugin.json`. Trust that project in Vibe Code, then start a session or run `/reload-plugins`. Open `/plugins` to inspect BrewPage and `/mcp` to inspect its remote server.

Vibe Code exposes the bundled skill as `/brewpage:brewpage-publish`. The MCP endpoint is `https://brewpage.app/mcp` over Streamable HTTP. Anonymous publishing needs no BrewPage account or API key. Normal Vibe approval rules apply to MCP tools.

## Existing skill compatibility

The eleven skill files under `skills/brewpage-publish/upstream/` come from [claude-brewcode v6.13.0 at `dd0bd63bc983fcb6c1c36f9ea3603eb014b9c97c`](https://github.com/kochetkov-ma/claude-brewcode/tree/dd0bd63bc983fcb6c1c36f9ea3603eb014b9c97c/skills/brewpage-publish). Their only change is the runner's User-Agent `brewpage-mistral-vibe/1.1.0 (+https://brewpage.app)`.

The [native adapter](skills/brewpage-publish/SKILL.md) prefers an exposed BrewPage MCP tool that supports the requested material and options, the selected owner and verified private result delivery. If MCP cannot support the request or its local bytes, the skill can select the authorized `run.py` launcher with the same owner before dispatch. An explicit MCP-only request stays pending without a compatible binding. Vibe's normal approvals apply. A refused write stays on its chosen route. An uncertain result must be reconciled before another write.

The launcher runs the bundled REST helper with absolute content and password paths and its own Mistral state. It isolates Claude and Git settings from the host session. Owner history and its sibling recovery receipt live under `$VIBE_HOME/brewpage-publish-state/`. The default history path is `~/.vibe/brewpage-publish-state/.claude/brewpage-history.md`, with a `0700` state directory and `0600` history. Run `python3 '<installed skill directory>/run.py' --check-isolation` to check local state without uploading content.

The skill returns the reader link and relevant notices. It delivers a management link or owner key only through a verified owner-only result and chat. Anyone holding the management link can edit or delete the page. The launcher reports a saved key after private readback and supports protected recovery.

## License and verification

The package and bundled skill use MIT. See [LICENSE](LICENSE). The distribution's `manifest.json` and `validation.json` record the seventeen-file archive roundtrip, syntax and isolated launcher checks, including protected owner recovery. Fresh native loading, tool discovery and model-driven publishing remain unverified for 1.1.0.

The package follows [Mistral's plugin documentation](https://docs.mistral.ai/vibe/code/cli/plugins). Plugin support is experimental. This CLI package is separate from any connector configured in Le Chat.

## Historical packages and checks

Version 1.0.0 was checked for native loading, skill exposure and MCP discovery without a model call or publication. Versions 1.0.1 through 1.0.6 retained schema, archive and launcher hash checks. Version 1.0.1 updated discovery metadata. Versions 1.0.2, 1.0.3 and 1.0.4 synced upstream commits `809e0fa2`, `48255159` and `5da825f1` respectively. Version 1.0.3 added reader and management receipt guidance, and 1.0.4 added Page data guidance. Versions 1.0.5 and 1.0.6 changed the version.
