---
name: brewpage-publish
description: Publish user-selected text, Markdown, JSON, files or built static sites through the connected BrewPage MCP tools, with explicit visibility and password choices.
license: MIT
---

# BrewPage publish

Adapted from the existing MIT-licensed BrewPage publishing skill. Publish the exact user-selected content through the connected BrewPage MCP tools. No BrewPage account or API key is required. The unchanged original files in `upstream/` document provenance; their Claude-specific commands are not this skill's execution path.

Use the connected BrewPage capability descriptions and input schemas to choose tools. Read the current limits first through the limits capability. If the required capability is unavailable, stop and explain what is missing; do not invent tool identifiers or silently switch to local scripts or direct HTTP.

Before publishing, identify the content type, show its size and a small preview or file manifest, and state the requested TTL. Default requested TTL is 15 days; respect current limits and the user's explicit choice. A returned existing publication may retain its earlier expiry; returned expiry metadata is authoritative.

Ask for an explicit namespace choice: `public`, a meaningful suggested private slug, or a custom private slug. Public publications are discoverable through the gallery and search; never publish secrets, tokens or personal data there. Private namespaces are unlisted and not indexed, but anyone with the link can read them unless password protected. A namespace contains 1–32 lowercase letters, digits or hyphens. Explicit Skip selects the suggested private slug; silence or ambiguity stops publication.

Ask separately for an explicit password choice: no password, or an existing local password file accessible through a secure supported capability. Explicit Skip means no password. Never request a password pasted into chat, read or print its contents, or place it in a prompt, URL or command argument. If the connected tools cannot securely consume the chosen password file, stop and explain the limitation. Reuse an earlier explicit choice only for the same content/workflow; never invent consent.

Choose the connected publication capability matching text/Markdown, JSON, a single file, or a built static site. Publish built output, never project sources. A site must contain an HTML entry; use the explicit entry choice, otherwise root `index.html`, otherwise the shallowest HTML file with name order breaking ties. Show the site manifest and resolved entry before upload. Exclude credentials, environment files, dependency/source trees, hidden/system files and symlinks from a directory bundle, except intended root `.well-known/` content. Never change a supplied ZIP silently.

For unexpected, hidden or sensitive archive entries, show the flagged manifest and obtain explicit approval tied to the exact archive SHA-256 before upload. Changed archive bytes require a fresh manifest, digest and approval. If the connected capability cannot inspect an archive or bind approval to its exact bytes, stop rather than bypassing that review. Do not claim an archive was checked without evidence.

Use the optional delivery mode only through the connected tool's documented parameter, never inside authored content. Otherwise use server defaults. Keep the returned publication identity and exact reader URL, including a trailing slash; never reconstruct a hostname from namespace or ID. Do not append passwords to URLs.

After success, report the exact reader URL, returned expiry and relevant notices. Owner tokens, owner links, management links and password material are credentials: never include them in public output or chat. Preserve owner capability only through a private supported storage mechanism; if none is available, do not claim it was saved and explain that limitation without revealing its value. Report a returned existing publication without an owner capability honestly.

Stop at the first rejected or failed mutation and report the tool's safe error message; do not retry, change content, or relax choices without a concrete correction or user instruction. A successful tool response proves publication; rendering requires a separate browser check. Do not publish test content merely to activate this skill.
