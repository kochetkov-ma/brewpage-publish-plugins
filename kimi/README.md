# BrewPage Publish for Kimi Code

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/latest"><img height="18" alt="GitHub release" src="https://img.shields.io/github/v/release/kochetkov-ma/brewpage-publish-plugins"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

Version 1.1.0 packages the native `kimi.plugin.json` and eleven skill files from [claude-brewcode v6.13.0](https://github.com/kochetkov-ma/claude-brewcode/tree/9581676113c40c7516504dada2b581fb761b0fec/skills/brewpage-publish), including four recipes. The bundled files differ from that commit only in the User-Agent `brewpage-kimi/1.1.0 (+https://brewpage.app)`. Kimi controls the User-Agent for its connected MCP requests.

## Install

Extract [brewpage-kimi-code-1.1.0.zip](brewpage-kimi-code-1.1.0.zip) into a directory named `brewpage-publish`, then install that directory in Kimi Code.

```text
/plugins install /absolute/path/to/brewpage-publish
/reload
/skill:brewpage-publish:brewpage-publish
```

## Publish

Use the bundled workflow to choose publication content, namespace, password and TTL. The native `skillInstructions` override selects connected BrewPage tools at `https://brewpage.app/mcp` exclusively. It leaves unsupported operations pending and asks directly for any missing namespace or password choice. The connected tools and Kimi's permissions govern execution.

Before a write that can return a private management link or owner key, the skill verifies owner-only result delivery or a protected handoff. A create that may issue a key also needs private storage or owner-only delivery arranged in advance. The skill returns the exact reader link and relevant notices. It delivers the management link and any owner proof privately, and confirms storage through private readback. Anyone with the management link can edit or delete the page. If the outcome is uncertain, the skill checks the selected owner's receipt or inventory before another write.

## Verification

[The 1.1.0 receipt](refresh-verification-1.1.0.json) records the twelve-file archive roundtrip, eleven synced upstream files and syntax checks. Fresh native import, model-driven publishing and private delivery on Kimi remain unverified for this version.

## Historical packages and checks

Versions 1.0.0 through 1.0.6 remain available. Version 1.0.1 updated display metadata. Versions 1.0.2, 1.0.3 and 1.0.4 synced upstream commits `809e0fa2`, `48255159` and `5da825f1` respectively. Version 1.0.3 made the reader and management links part of the result instructions. Versions 1.0.5 and 1.0.6 changed the version and retained the MCP-only override. The [directory manifest](directory-manifest.json) lists the archived packages and verification receipts.

Native verification used official npm package `@moonshot-ai/kimi-code@2.3.3`, Node.js `24.19.0`, a clean environment, an isolated temporary Kimi home and the authenticated loopback Server API. Import returned `state=ok`, one skill, one enabled HTTP MCP server, no errors and no diagnostics. Native MCP connection discovery returned 20 tools. All seven installed source hashes matched.

The historical manifest was reimported after the output and storage override changed. Its exact `skillInstructions` matched the official server-normalized import result, and six output and storage clauses passed local contract assertions. The pinned 2.3.3 `renderSkillPrompt` method and six extracted dependencies rendered the override before the immutable source and showed how it superseded the old Step 7 instruction.

The native receipt covers the 1.0.0 baseline. [metadata-verification.json](metadata-verification.json) records the 1.0.1 metadata parser, archive roundtrip and seven source hashes. The override import and rendering checks cover 1.0.0 through 1.0.2. Native verification of the revised 1.0.3 result rule and model-driven publication remained pending.

This guide covers the Kimi Code package. The historical checks covered local plugin installation. Consumer Kimi Work registration and marketplace acceptance are separate. The links below include the consumer publication instructions and the Kimi Code marketplace discussion.

Sources:

- https://www.kimi.com/code/docs/en/kimi-code-cli/guides/getting-started.html
- https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html
- https://www.kimi.com/code/docs/en/kimi-code-cli/reference/server-api.html
- https://www.kimi.com/en/help/plugins-and-skills/publish
- https://github.com/MoonshotAI/kimi-code/issues/1566

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
