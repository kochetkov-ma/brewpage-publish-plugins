# BrewPage plugin for Google Antigravity

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme).

Publish HTML, Markdown, files and static sites from Antigravity (App, CLI or IDE
extensions) to [brewpage.app](https://brewpage.app) and get an HTTPS link back.
No account or API key. Publications are temporary: 15 days by default.

BrewPage is a hosted, closed-source service. This plugin is MIT-licensed.

## What is inside

| Part | Path | What it does |
|------|------|--------------|
| Manifest | `plugin.json` | Antigravity plugin manifest (`https://antigravity.google/schemas/v1/plugin.json`) |
| MCP servers | `mcp_config.json` | `brewpage`: the remote server `https://brewpage.app/mcp` (Streamable HTTP, no sign-in), enabled. `brewpage-local`: `npx -y brewpage-mcp@1.19.0` over stdio, disabled; turn it on in `/mcp` if your network blocks the remote server (needs Node.js 20+) |
| Skill | `skills/brewpage-publish/SKILL.md` | Tells the agent when to publish, which tool to call and what to ask first (namespace, password, TTL) |
| Logo | `assets/logo.svg` | BrewPage mark |

Tools appear as `brewpage_brewpage` (`publish_html`, `publish_file`, `publish_site`,
`publish_json`, `publish_kv`, `update_html`, `republish_site`, `delete_resource`,
`get_limits`, `search_gallery` and more). A page or site can also save what its
visitors enter (Page data): the agent publishes it with `state` and reads the entries
with `get_page_data`; you read them in the Data tab of the management link.

## Install

```
agy plugin install https://github.com/kochetkov-ma/brewpage-publish-plugins/tree/main/integrations/antigravity-plugin
agy plugin list
```

From a local clone: `agy plugin install ./integrations/antigravity-plugin`.

Then ask, for example, "Publish this report as a private BrewPage page and give me
the link", or run `/brewpage-publish`.

## Privacy

- Namespace `public` is listed in the gallery and sitemap and can be indexed by
  search engines. Any other namespace is private: unlisted, not indexed, open to
  anyone with the link; add a password to restrict it.
- Each publish returns a management link and an owner token. The agent gives you
  the management link; it is private: anyone who has it can edit or delete the page.
  The owner token updates or deletes the publication through the tools.
- [Privacy policy](https://brewpage.app/privacy), [terms](https://brewpage.app/terms).

## Validation

`agy plugin validate --strict` with Antigravity CLI 1.5.3 passes with 0 errors and
0 warnings.

## Support and license

Questions: [info@brewpage.app](mailto:info@brewpage.app). MIT; see [LICENSE](LICENSE).
