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

Give the user the returned link and the `MANAGE LINK` (`manageUrl`; private: anyone
who has it can edit or delete the page). Keep the owner token for `update_html`,
`republish_site` and `delete_resource`, and show it when the user asks or when you
cannot keep it. Never post either publicly (public page, repo, shared channel).

## Pages that save data

A published HTML page or site can save what its visitors enter (game progress, form
answers, guestbook messages, votes): Page data. Call `get_guide` before writing such
a page, load `https://brewpage.app/js/state.js` in it and publish with `state` on
`publish_html` or `publish_site` (`update_html` and `republish_site` change it).
`get_page_data`, `set_page_data`, `configure_page_data` and `delete_page_data` read,
write, configure and delete entries; they take the owner token, or the management
link as `manageUrl`. The author also reads entries in the Data tab of the management
link.

## Fallback

If the remote `brewpage_brewpage` server is unreachable, the user can enable the
`brewpage-local` server (runs `npx -y brewpage-mcp`, needs Node.js 20+) in `/mcp`.
