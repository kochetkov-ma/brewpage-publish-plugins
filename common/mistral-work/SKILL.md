---
name: brewpage-publish
description: HTML hosting, static sites and AI artifact publishing; share Markdown, documents, reports and any files through HTTPS links. Publish user-selected content through connected BrewPage MCP tools, with explicit visibility and password choices.
license: MIT
---

# BrewPage publish

Adapted from the existing MIT-licensed BrewPage publishing skill. Publish the exact user-selected content through the connected BrewPage MCP tools. No BrewPage account or API key is required. The unchanged original files in `upstream/` document provenance; their Claude-specific commands are not this skill's execution path.

Use the connected BrewPage capability descriptions and input schemas to choose tools. Read the current limits first through the limits capability. If the required capability is unavailable, stop and explain what is missing; do not invent tool identifiers or silently switch to local scripts or direct HTTP.

Before a write that can return an owner token or private management link, verify that the MCP result goes only to the requesting owner or an authorized protected handoff. A verified owner-only interaction can establish this boundary. A private store filled after shared tool output does not protect that output. Arrange authorized private storage or owner-only delivery for newly issued proof before publishing. If the host cannot verify these conditions, leave the publication pending and name the missing capability.

Before publishing, identify the content type, show its size and a small preview or file manifest, and state the requested TTL. Default requested TTL is 15 days; respect current limits and the user's explicit choice. A returned existing publication may retain its earlier expiry; returned expiry metadata is authoritative.

Ask for an explicit namespace choice: `public`, a meaningful suggested private slug, or a custom private slug. Public publications are discoverable through the gallery and search; never publish secrets, tokens or personal data there. Private namespaces are unlisted and not indexed, but anyone with the link can read them unless password protected. A namespace contains 1–32 lowercase letters, digits or hyphens. Explicit Skip selects the suggested private slug; silence or ambiguity stops publication.

Ask separately for an explicit password choice: no password, or an existing local password file accessible through a secure supported capability. Explicit Skip means no password. Never request a password pasted into chat, read or print its contents, or place it in a prompt, URL or command argument. If the connected tools cannot securely consume the chosen password file, stop and explain the limitation. Reuse an earlier explicit choice only for the same content/workflow; never invent consent.

Choose the connected publication capability matching text/Markdown, JSON, a single file, or a built static site. Publish built output, never project sources. A site must contain an HTML entry; use the explicit entry choice, otherwise root `index.html`, otherwise the shallowest HTML file with name order breaking ties. Show the site manifest and resolved entry before upload. Exclude credentials, environment files, dependency/source trees, hidden/system files and symlinks from a directory bundle, except intended root `.well-known/` content. Never change a supplied ZIP silently.

Remove owner history, recovery receipts, credential files and other protected inputs from a directory build. If a supplied archive contains protected entries, request a clean archive before publishing. For other unexpected archive entries, obtain explicit approval tied to the flagged manifest and its exact SHA-256. Changed bytes need a fresh review. Leave the publication pending if the connected capability cannot perform or bind the required inspection.

Use the optional delivery mode only through the connected tool's documented parameter, never inside authored content. Otherwise use server defaults. Keep the returned publication identity and exact reader URL, including a trailing slash; never reconstruct a hostname from namespace or ID. Do not append passwords to URLs.

After success, give the exact reader URL, the returned expiry and relevant notices. Provide the returned management link through the verified owner-only channel or protected handoff. Anyone with that link can manage the page. Claim an owner token was saved after private readback. Otherwise complete the agreed private handoff and state whether it was saved. Keep owner capabilities and passwords out of shared output. If the result did not grant owner access, report that limitation.

Stop at the first rejected mutation and report the safe reason. If the result is uncertain, reconcile through the selected owner's receipt or inventory before another write. Keep the selected owner and MCP route. Rendering requires a separate browser check. Use the skill for user-selected content.
