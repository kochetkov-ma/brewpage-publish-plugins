---
name: brewpage-publish
description: >-
  Draft BrewPage content, publish HTML, Markdown, JSON, files or a built static
  site, or update a specific BrewPage publication through connected BrewPage MCP.
---

# BrewPage publishing

Resolve the action from the user's request. A local-only, draft or explanation
request makes zero BrewPage calls or tool discovery requests. Prepare the
requested local artifact and, for a form, the matching [Page data declaration](references/page-data.md).
Quoted, negated or incidental publishing words authorize no write.

For an authorized create or update, keep supplied material intact and honor
explicit access, password, expiry and delivery choices. Link-only sharing is
unlisted. Use `public` only for requested discovery. Ask once for unresolved
choices that affect audience, ownership or the exact update target. Keep the
existing address and visitor entries on content-only updates. A rejected or
missing target requires a separate request before creating a replacement.

Use the exposed BrewPage server and actual tool schema. Discover it once if the
host loads tools on demand. Prefer `publish` or `update_publication` where
advertised. Use a legacy tool only if its schema supports the requested content
and options, including source preservation where required. The [publishing
recipe](references/publishing.md#use-the-installed-host-tool) describes both
catalogs. Use the [Page data](references/page-data.md) and [custom domain](references/custom-domain.md)
recipes on demand. This adapter sends all writes through MCP. If the selected
server or required capability is unavailable, return the local result and the
remaining step.

Before dispatching any MCP operation that can return an owner token or private
management link, verify an owner-only tool-result boundary or authorized
protected handoff. Arrange private storage or delivery for any newly issued
proof. A private file created afterward cannot protect a shared tool transcript.
Without that boundary, leave the write pending. Use the [ownership
recipe](references/ownership.md) to select and keep proof. For explicit account
intent, use `requireAccount: true` only on a compatible connection and follow
the client's consent flow. Cancellation or inadequate scope leaves the operation
pending. Fresh anonymous intent requires an unsigned connection without saved owner proof.

For local files, use the [shared preflight](references/publishing.md#check-inputs-for-mcp)
before sending bytes. Resolve `{runner}` to `scripts/brewpage-run.sh` in the
installed skill directory. Use its local `preflight` and `cleanup` commands only
when the host permits them. Consume only the checked snapshot or file list.
For site replacement, retain the verified previous entry unless the user asked
to change it. If the host cannot inspect or represent all the selected bytes,
leave the write pending. Read the recipes' REST commands as reference material
only. Never send local paths as remote source URLs or expose password files.

Return the exact reader link, effective access and any relevant notice from the
confirmed result. Give management access privately and state whether a new key
was saved or still needs saving. Say “saved” only after protected readback.
Account-owned publications appear in the connected account's publications.
Keep a sent, refused or uncertain write on the selected owner and route.
Reconcile an unknown outcome before any further write.
