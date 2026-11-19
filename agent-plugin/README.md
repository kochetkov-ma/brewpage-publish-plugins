# BrewPage agent plugin

Draft locally, publish supplied material or a newly authored page, and update an
existing BrewPage publication from your coding agent. [BrewPage](https://brewpage.app)
hosts HTML, Markdown, JSON, files and built static sites. You can publish without
an account.

| Part | Path | Host |
|------|------|------|
| Claude Code manifest | `.claude-plugin/plugin.json` | Claude Code, Grok Build |
| Cursor manifest | `.cursor-plugin/plugin.json` | Cursor |
| Agent Plugins manifest | `plugin.json` | GitHub Copilot and compatible Agent Plugins hosts |
| MCP configuration | `.mcp.json`, `mcp.json` | Streamable HTTP at `https://brewpage.app/mcp` |
| Skill | `skills/brewpage-publish/` | Bundled workflow, recipes and local runner |

The skill ships the eleven reviewed OpenClaw source members with the User-Agent
`brewpage-agent-plugin/1.1.1 (+https://brewpage.app)`. [Source and file digests](PROVENANCE.json)

## Install

For Claude Code, add this repository as a marketplace and install its BrewPage
plugin. To test this candidate, register a local checkout as the marketplace.

```
/plugin marketplace add /path/to/brewpage-publish-plugins
/plugin install brewpage@brewpage
```

Grok Build also reads Claude Code plugins. Load the candidate directly with
`grok --plugin-dir /path/to/brewpage-publish-plugins/agent-plugin`. Version 1.1.1
is a release candidate. Marketplace availability applies to the published version.

## Use it

- “Draft an RSVP page for BrewPage, local only” prepares an artifact locally.
- “Publish `report.html` as an unlisted page” shares the supplied material.
- “Create and publish an unlisted poll that saves answers” includes Page data.
- “Update this BrewPage publication with `report.html`” edits the exact owned target.

The skill checks the host's actual BrewPage tools before a write. It prefers
compatible MCP and can select the bundled REST runner when the host permits it
and the selected owner proof works on that route. A compatible MCP client can
connect an account on request. The skill keeps an uncertain write pending while
it reconciles the result through the selected owner. [Skill and recipes](skills/brewpage-publish/SKILL.md)

Before sending local files, the skill checks a snapshot. Owner histories,
credentials and recovery receipts stay outside uploads. An ordinary REST
receipt gives the reader link, effective access, notices and storage status.
The workspace store is an owner-only, Git-ignored `brewpage-history.md`.
Credential-bearing MCP output and private receipts require a verified owner-only
channel or an authorized protected handoff. [Ownership and recovery](skills/brewpage-publish/references/ownership.md)

Anyone with an unlisted link can open it unless password protection applies.
Use the actual returned link and access state. Current limits are available
through the MCP limits capability or the [limits API](https://brewpage.app/api/limits).

The local runner uses a POSIX environment with Bash, curl, jq, Python 3 and
Git in a checkout. Local file and site checks also use Node.js, zip and unzip.

Support: [info@brewpage.app](mailto:info@brewpage.app). This plugin is [MIT-licensed](LICENSE).
BrewPage is a hosted service. [Privacy policy](https://brewpage.app/privacy) · [Terms](https://brewpage.app/terms)
