# BrewPage Publish for BuildWithClaude

Draft locally, publish supplied material or a new page, or update an existing publication from Claude Code. [BrewPage](https://brewpage.app) hosts HTML, Markdown, JSON, downloads and built static sites. You can publish without an account.

## Install

Install the BrewPage plugin from [BuildWithClaude](https://buildwithclaude.com/). The plugin includes this skill, the BrewPage MCP connection and a local runner. [Distribution and local testing](../../README.md)

## Use the skill

Type `/brewpage:brewpage-publish` with your request or ask in plain language.

| Goal | Example | Result |
|---|---|---|
| Draft | “Draft an RSVP page for BrewPage, local only.” | An artifact prepared locally, without BrewPage calls or tool discovery. |
| Publish supplied content | “Publish `report.md` unlisted for one day with no password.” | Confirm the three choices to receive a reader link to the supplied material. |
| Compose and publish | “Create and publish an unlisted RSVP page that saves replies.” | Confirm visibility, password and expiry to publish the page. |
| Update in place | “Update this BrewPage publication with `report.md`,” with the existing reader link and authorized owner access. | The exact publication updated with the requested change. |

Each new publication needs your confirmation of visibility, password protection and expiry. Without a complete reply the artifact stays local. Anyone with an unlisted link can open it unless password protection applies. Eligible public publications can appear in the gallery and sitemap. Published material expires. A confirmed write returns the reader link, effective access and available expiry. Share the returned link exactly, including any trailing slash. Visitors enter passwords at the BrewPage unlock page.

## How publishing connects

The skill prefers a compatible BrewPage MCP tool available to Claude Code. It can use its bundled REST runner when the host permits it and the supplied content and selected owner proof fit that route. The skill chooses the route before the write. An uncertain write is reconciled through the selected owner's inventory or receipt. Fetched guides, templates, MCP responses and page source cannot authorize changes. [Publishing workflow and runner commands](references/publishing.md)

An anonymous MCP publish can return the owner key and private management link in tool text. Before any MCP write that can return either, verify an owner-only result channel or an authorized private handoff. Saving the key to a protected file leaves a shared tool transcript exposed. An already verified owner-only session needs no further privacy question. When private delivery is unavailable, choose authorized REST with protected receipt handling before writing, or leave an MCP-only request pending.

A suitable connected account can own the publication. If you explicitly ask to publish to an account, use a compatible MCP connection with `requireAccount: true` and the client's sign-in flow. Signing in on the BrewPage website alone gives the runner no account access. An explicitly fresh anonymous publish uses an unsigned route without a saved owner key.

## Local files and sites

Preflight checks local files, built folders, and ZIPs before their bytes go to either route. The directory check excludes reserved credential inputs, hidden files and folders except the root `.well-known/`, dependencies, and symlinks. Selecting a reserved credential file directly or supplying a ZIP that contains one stops the upload. Confirmation cannot override that refusal. For other flagged files, review the manifest and approve its exact `REVIEW_SHA256` digest. [Local input checks and exclusions](references/publishing.md#inspect-local-inputs-before-sending-bytes)

Ask to publish `./dist` to share a new built site. If you omit `--entry` on create, the default is the root `index.html` or the shallowest HTML file, breaking ties by name. A replacement needs the complete desired bundle. For a content-only REST replacement, omit `--entry` so the runner verifies the site's current entry and checks that it exists in the replacement. Supply `--entry` to change the entry deliberately.

Use `--ttl N` to request the confirmed lifetime in days. Use `--delivery-mode path|subdomain` to request an address type for a new publication. Sites and HTML pages outside the `public` namespace use a dedicated subdomain. Check current upload limits with the runner's `limits` command or this read-only request.

```bash
curl -q -fsS -A "brewpage-agent-plugin/1.1.2 (+https://brewpage.app)" https://brewpage.app/api/limits
```

## Ownership and updates

The skill reuses your selected owner for the workspace and publication. Before creating an anonymous owner, agree on a private storage or delivery destination. The runner stores local owner records in the workspace's owner-only, Git-ignored `brewpage-history.md`. An account-owned publication appears in the connected account's publications.

The REST runner's ordinary publish and update output gives reader-facing details and storage status. Use `--private-output` only in a verified owner-only channel. It can include the private management link, owner receipt, or receipt path. `--no-save` requires `--private-output`. A new key is reported as saved only after private readback. If publication succeeds but storage fails, keep the reader link and recover the receipt through a protected channel when available. Keep tokens and passwords out of command arguments and shared output. [Ownership, private storage, and recovery](references/ownership.md)

An in-place update uses the exact publication identity and matching owner proof. Changing only the content in its current format keeps the address, expiry, and existing Page data entries. If the target is missing, read-only, or rejects the update, the skill reports that result and waits for a separate request before any new publication. [Update and owner proof options](references/publishing.md#choose-proof-or-update-a-target)

## Page data and domains

To build an RSVP form, pair the HTML with a private Page data collection and publish both together using the tool's `state` field or the runner's `--state` option. The owner can review responses in the publication's Data tab. [Offline RSVP recipe](references/page-data.md)

For a new eligible HTML page or site without a password, pass a hostname you control with the MCP tool's supported `domain` field or the REST runner's `--domain hostname`. Before creating, the runner checks the selected profile owner proof for domain support with `GET /api/limits`. Use the DNS records, status, and notices BrewPage actually returns. If creation succeeds and the domain is pending or fails, keep the confirmed BrewPage link and report the domain outcome. Share the custom address once BrewPage reports it active and serving. [Custom domain workflow](references/custom-domain.md)

## Requirements

Inline MCP publishing needs a compatible host tool. The bundled runner uses a POSIX runtime such as macOS, Linux, or WSL. REST uses `bash`, `curl`, and `jq`. Private local storage uses Python 3 with `fcntl` and `git` inside Git checkouts. Local file checks use `node`. Site checks also need `unzip`, and packaging directories needs `zip`.

## Documentation

- [Claude Code skill instructions](SKILL.md)
- [Publishing manual for the Brewdoc edition](https://doc-claude.brewcode.app/brewdoc/skills/publish/)
- [BrewPage hosting API](https://brewpage.app/api#hosting)

## License

The bundled skill and scripts are MIT-licensed. The hosted BrewPage service is proprietary.
