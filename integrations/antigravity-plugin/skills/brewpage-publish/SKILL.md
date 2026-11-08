---
name: brewpage-publish
description: >-
  Publish HTML, Markdown, text, a file or a multi-file static site to brewpage.app
  (free hosting, no sign-up) and return a public HTTPS link. Use when the user asks
  to publish, share a link, host a page or report, paste text online, upload a file
  or deploy a built site.
---

# brewpage-publish

Publish content to **brewpage.app** with the bundled BrewPage MCP tools
(`brewpage_brewpage` server). No account or API key is needed.

## When to use

- The user asks to publish, share, host or "give me a link" for a page, report,
  document, Markdown, a file or a built static site.
- The user wants an agent result (HTML report, chart, summary) viewable in a browser.

Never publish without the user's request, and never publish secrets, tokens or
personal data to the `public` namespace.

## Pick the tool

| Content | Tool |
|---------|------|
| HTML document, Markdown, plain text, code | `publish_html` (`format`: `html`, `markdown`, or omit to auto-detect) |
| A file reachable by URL | `publish_file` |
| A built static site (folder with `index.html`), or one HTML entry plus assets | `publish_site` |
| Structured data | `publish_json` or `publish_kv` |
| Current size and TTL limits | `get_limits` |

Publish built output (`dist/`, `build/`, `out/`, `_site/`, `public/`), never project
sources. A site needs at least one `.html` file.

Pass the exact content, never a summary of it.

## Ask before publishing

1. **Namespace.** Ask:
   - `public`: listed in the public gallery and sitemap, so Google, Bing and AI search
     can find it. Use for docs, guides, demos, portfolios, reports meant to be shared.
   - a private slug (suggest a short meaningful one, such as `api-docs` or `report-q2`;
     1-32 lowercase letters, digits or hyphens): unlisted and not indexed; anyone with
     the link can still open it.
   An empty or unclear answer means stop. Never infer consent from silence.
2. **Password** (optional): restricts who can open a private page.
3. **TTL**: 15 days by default; pass `ttlDays` only when the user names a period.

## After publishing

Return the link from the tool result. The result also carries an owner token:
tell the user to keep it, because `update_html`, `republish_site` and
`delete_resource` need it. Do not store it anywhere else.

## Fallback

If the remote `brewpage_brewpage` server is unreachable, the user can enable the
`brewpage-local` server (runs `npx -y brewpage-mcp`, needs Node.js 20+) in `/mcp`.
