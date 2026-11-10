# BrewPage agent plugin

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for [BrewPage](https://brewpage.app).

Publish HTML, Markdown, any file or a multi-file static site from an AI coding
agent to [brewpage.app](https://brewpage.app) and get an HTTPS link back.
Publishing needs no account and no API key.

BrewPage is a hosted, closed-source service. This plugin (manifests, skill and
scripts) is MIT-licensed.

## What is inside

| Part | Path | Read by |
|------|------|---------|
| Claude Code manifest | `.claude-plugin/plugin.json` | Claude Code, Grok Build |
| Cursor manifest | `.cursor-plugin/plugin.json` | Cursor |
| Agent Plugins manifest | `plugin.json` | Agent Plugins hosts (GitHub Copilot, Cursor) |
| MCP server | `.mcp.json` (Claude format), `mcp.json` (Agent Plugins format) | The BrewPage remote MCP server, `https://brewpage.app/mcp` (Streamable HTTP, no sign-in) |
| Skill | `skills/brewpage-publish/` | Detects the content type, asks for namespace and password, uploads through `scripts/brewpage-run.sh`, returns the link |
| Icon | `assets/icon.svg` | BrewPage mark |

The skill is the MIT-licensed BrewPage publishing skill from
[kochetkov-ma/claude-brewcode](https://github.com/kochetkov-ma/claude-brewcode)
(`openclaw/brewpage-publish`, commit `9ddf5c045b576a3b6493b37dc1743fa3015b5a22`),
with its User-Agent set to `brewpage-agent-plugin/0.1.0` and one change on top:
after publishing it also returns the management link.

## Install

Claude Code:

```
/plugin marketplace add kochetkov-ma/brewpage-publish-plugins
/plugin install brewpage@brewpage
```

Grok Build reads Claude Code plugins; load a local checkout with
`grok --plugin-dir /path/to/brewpage-publish-plugins/agent-plugin`.

## Use it

Ask in natural language:

```
Publish report.html to BrewPage and give me the link
Share this Markdown summary as a BrewPage page that expires in 7 days
Upload the ./dist folder to BrewPage as a site
```

The skill asks for a namespace (`public` lists the page in the gallery; a private
slug, the default, keeps it unlisted) and an optional password file, uploads, and
gives you the page link and the management link. See
[the skill workflow](skills/brewpage-publish/SKILL.md).

| Content | API |
|---------|-----|
| Text, Markdown, `.md` file | `POST /api/html?format=markdown` |
| Whole HTML document, `.html` file | `POST /api/html?format=html` |
| Any other file | `POST /api/files` |
| Built static directory or `.zip` | `POST /api/sites` |

## Limits

Pages expire: default 15 days, 1 to 30 days (up to 90 with an optional free profile
at [account.brewpage.app](https://account.brewpage.app)). Current values:
`https://brewpage.app/api/limits`.

## Privacy

- An unlisted link is not private: anyone with the link can open it. Never publish
  secrets, credentials or personal data, and use `public` only for content meant to
  be found.
- Each publish returns a management link and an owner token. The assistant gives
  you the management link; it is private: anyone who has it can edit or delete the
  page. The skill writes the token to `./brewpage-history.md` (mode 600, added to
  `.gitignore`) and the assistant shows it when you ask. Neither is ever posted
  publicly (public page, repo, shared channel).
- Network endpoints: only `brewpage.app` (REST API and `https://brewpage.app/mcp`).
  No credentials are needed.
- [Terms](https://brewpage.app/terms), [Privacy](https://brewpage.app/privacy).

## Requirements

macOS, Linux or WSL with `bash`, `curl`, `jq` and `python3`; sites also need `node`,
`zip` and `unzip`. The scripts use no third-party packages.

Support: [info@brewpage.app](mailto:info@brewpage.app)

## License

MIT, see [LICENSE](LICENSE). The hosted BrewPage service is proprietary.
