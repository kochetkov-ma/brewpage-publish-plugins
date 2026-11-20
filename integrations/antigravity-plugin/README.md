# BrewPage plugin for Google Antigravity

Draft BrewPage content locally, publish supplied or newly authored material, or
update a specific owned publication. Share the HTTPS reader link BrewPage returns.
You can publish without an account. A compatible MCP client can connect an
account when requested.

| Part | What it does |
|------|--------------|
| `plugin.json` | Antigravity plugin manifest |
| `mcp_config.json` | Enabled BrewPage HTTPS MCP at `https://brewpage.app/mcp` and disabled optional local stdio |
| `skills/brewpage-publish/` | MCP publishing workflow, shared recipes and local file preflight |

## Install and use

Validate and install the 1.1.2 candidate from a local checkout using the
[Antigravity plugin CLI](https://antigravity.google/docs/build-plugins).

```
agy plugin validate --strict ./integrations/antigravity-plugin
agy plugin install ./integrations/antigravity-plugin
agy plugin list
```

Ask “Publish this report as an unlisted BrewPage page and give me the link,”
or invoke `/brewpage-publish`. A local draft makes no BrewPage calls. The skill
uses the BrewPage tools actually available in the session. Built sites and local
files need the shared preflight in a host that allows the installed helper to
read the selected input and temporary snapshot. [Skill and recipes](skills/brewpage-publish/SKILL.md)

`brewpage-local` may be enabled before a write when it supports the selected
owner and request. It runs `npx -y brewpage-mcp@3.0.0` with Node.js 20 or newer.
That pin requires MCP 3.0.0 to be published to the npm registry. The process
still needs access to BrewPage's HTTPS service. A sent or uncertain write
remains on its selected route for reconciliation.

Anyone with an unlisted link can open it unless password protection applies.
A new anonymous owner key and private management link require a verified
owner-only tool result or authorized protected handoff before publishing.
The skill confirms storage after protected readback. [Ownership and receipts](skills/brewpage-publish/references/ownership.md)

The shared local checker and recipes come from the reviewed BrewPage skill.
[Source and file digests](PROVENANCE.json)

Support: [info@brewpage.app](mailto:info@brewpage.app). This plugin is [MIT-licensed](LICENSE).
[Privacy policy](https://brewpage.app/privacy) · [Terms](https://brewpage.app/terms)
