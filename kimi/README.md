# BrewPage Publish for Kimi Code

Native `kimi.plugin.json` packages the existing BrewPage skill with its remote MCP service. The seven files in `skills/brewpage-publish/` are byte-identical to public source commit `d2d42282fecec988447f9c9547959b31a8012644` in `kochetkov-ma/claude-brewcode`.

Install from an extracted directory in Kimi Code:

```text
/plugins install /absolute/path/to/brewpage-publish
/reload
/skill:brewpage-publish:brewpage-publish
```

Use the bundled workflow to choose publication content, namespace, password and TTL. Publishing uses `https://brewpage.app/mcp`. The manifest's `skillInstructions` is a native MCP-only override: all bundled shell helpers, `CLAUDE_SKILL_DIR` expansion and Claude runtime assumptions are prohibited. Claude tool names and frontmatter grant no Kimi permissions. `AskUserQuestion` becomes an explicit user question; unanswered namespace/password choices stop publication. An unsupported MCP operation stops without a shell fallback. Owner tokens and management links stay private.

The override supersedes every Claude history, storage and output instruction, including Step 7. It prohibits reading or writing Claude configuration/history and repeating the original token-saved line. A saved-capability claim requires evidence of native private storage; without that evidence, report the not-persisted limitation without exposing a token or management URL. These are instructions to the agent, not an enforced sandbox. Native private storage and model compliance remain unverified.

Native verification used official npm package `@moonshot-ai/kimi-code@2.3.3`, Node.js `24.19.0`, a clean environment, an isolated temporary Kimi home and the authenticated loopback Server API. Import returned `state=ok`, one skill, one enabled HTTP MCP server, no errors and no diagnostics. Native MCP connection discovery returned 20 tools. All seven installed source hashes matched.

The final manifest was reimported after the output/storage override changed. Its exact `skillInstructions` matched the official server-normalized import result; six explicit output/storage clauses passed local contract assertions. The exact `renderSkillPrompt` method and six dependencies extracted from official 2.3.3 also rendered that override before the immutable source, reproducing the old Step 7 line and its native supersession. This validates imported/rendered instructions, not model behavior.

This proves package import and MCP tool discovery. No model invocation, authentication copy, paid operation or publication was performed. End-to-end model-driven publishing remains unverified.

This package is a Kimi Code plugin. It is not registered in a consumer Kimi account and has not been submitted to the Kimi official marketplace. The documented consumer publication application requires a created and basic-tested personal plugin in Kimi Work. Kimi Code's public third-party marketplace intake remains undocumented; official repository issue #1566 is open.

Sources:

- https://www.kimi.com/code/docs/en/kimi-code-cli/guides/getting-started.html
- https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html
- https://www.kimi.com/code/docs/en/kimi-code-cli/reference/server-api.html
- https://www.kimi.com/en/help/plugins-and-skills/publish
- https://github.com/MoonshotAI/kimi-code/issues/1566
- https://github.com/kochetkov-ma/claude-brewcode/tree/d2d42282fecec988447f9c9547959b31a8012644/skills/brewpage-publish
