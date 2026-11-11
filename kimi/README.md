# BrewPage Publish for Kimi Code

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

Native `kimi.plugin.json` packages the existing BrewPage skill with its remote MCP service. The seven files in `skills/brewpage-publish/` are synced from public source commit `5da825f1d535d9658f0de0893529c6ce06a613a5` in `kochetkov-ma/claude-brewcode`; the only deviation is the User-Agent value `brewpage-kimi/1.0.4 (+https://brewpage.app)`.

Version `1.0.1` updates plugin display metadata: host HTML pages and static sites, publish AI artifacts, and share Markdown, documents, reports or any file. The immutable active skill and the complete MCP security override remain unchanged. Version `1.0.2` synced the bundled skill to upstream `809e0fa2`. Version `1.0.3` synced it to upstream `48255159` (claude-brewcode v6.12.11) and changed the override's output rule: the agent gives you the reader URL and the management link. Version `1.0.4` syncs it to the commit above (claude-brewcode v6.12.12), which explains page data; the override is unchanged. The override stays MCP-only, so the bundled helpers stay unused. Extract `brewpage-kimi-code-1.0.4.zip`; the exact `1.0.0` to `1.0.3` archives are retained. `refresh-verification-1.0.4.json` records the 1.0.4 checks, `refresh-verification-1.0.3.json` the 1.0.3 checks, `refresh-verification-1.0.2.json` the 1.0.2 checks.

Install from an extracted directory in Kimi Code:

```text
/plugins install /absolute/path/to/brewpage-publish
/reload
/skill:brewpage-publish:brewpage-publish
```

Use the bundled workflow to choose publication content, namespace, password and TTL. Publishing uses `https://brewpage.app/mcp`. The manifest's `skillInstructions` is a native MCP-only override: all bundled shell helpers, `CLAUDE_SKILL_DIR` expansion and Claude runtime assumptions are prohibited. Claude tool names and frontmatter grant no Kimi permissions. `AskUserQuestion` becomes an explicit user question; unanswered namespace/password choices stop publication. An unsupported MCP operation stops without a shell fallback. After publishing the agent gives you the reader URL and the management link; the management link is private: anyone who has it can edit or delete the page.

The override supersedes every Claude history, storage and output instruction, including Step 7. It prohibits reading or writing Claude configuration/history and repeating the original token-saved line. A saved-token claim requires evidence of native private storage; without that evidence the agent gives you the owner token with the same privacy note and says it was not persisted. A stored token is shown when you ask. Neither the management link nor the token is posted publicly (public page, repo, shared channel). These are instructions to the agent, not an enforced sandbox. Native private storage and model compliance remain unverified.

Native verification used official npm package `@moonshot-ai/kimi-code@2.3.3`, Node.js `24.19.0`, a clean environment, an isolated temporary Kimi home and the authenticated loopback Server API. Import returned `state=ok`, one skill, one enabled HTTP MCP server, no errors and no diagnostics. Native MCP connection discovery returned 20 tools. All seven installed source hashes matched.

The final manifest was reimported after the output/storage override changed. Its exact `skillInstructions` matched the official server-normalized import result; six explicit output/storage clauses passed local contract assertions. The exact `renderSkillPrompt` method and six dependencies extracted from official 2.3.3 also rendered that override before the immutable source, reproducing the old Step 7 line and its native supersession. This validates imported/rendered instructions, not model behavior.

This proves package import and MCP tool discovery. No model invocation, authentication copy, paid operation or publication was performed. End-to-end model-driven publishing remains unverified.

Native verification above records the `1.0.0` baseline. `metadata-verification.json` records `1.0.1` validation with the actual pinned Kimi `2.3.3` metadata parser functions, archive roundtrip and all seven source hashes. It does not claim a repeated native import, official catalog indexing or model execution. The import and rendering checks above cover the override text of `1.0.0` to `1.0.2`; the `1.0.3` output rule was not reimported or rendered natively.

This package is a Kimi Code plugin. It is not registered in a consumer Kimi account and has not been submitted to the Kimi official marketplace. The documented consumer publication application requires a created and basic-tested personal plugin in Kimi Work. Kimi Code's public third-party marketplace intake remains undocumented; official repository issue #1566 is open.

Sources:

- https://www.kimi.com/code/docs/en/kimi-code-cli/guides/getting-started.html
- https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html
- https://www.kimi.com/code/docs/en/kimi-code-cli/reference/server-api.html
- https://www.kimi.com/en/help/plugins-and-skills/publish
- https://github.com/MoonshotAI/kimi-code/issues/1566
- https://github.com/kochetkov-ma/claude-brewcode/tree/5da825f1d535d9658f0de0893529c6ce06a613a5/skills/brewpage-publish

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
