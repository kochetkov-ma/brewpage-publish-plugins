# BrewPage for BuildWithClaude

Draft locally, publish approved HTML, Markdown, files or sites, and update an existing BrewPage publication from Claude Code. You can publish without an account.

Before every new upload, the skill asks you to confirm visibility, password protection and expiry. Without a complete reply the artifact stays local. Anyone with the link can open it unless password protection is enabled. Eligible public content can appear in the gallery and sitemap. Published content expires.

## Install and run

After [BuildWithClaude](https://buildwithclaude.com/) lists version 1.1.4, install it from Claude Code.

```text
/plugin install brewpage --marketplace davepoon/buildwithclaude
```

To try the exact package locally, extract the release archive and run `claude --plugin-dir /absolute/path/to/brewpage-buildwithclaude`.

- Ask “Draft a schedule for BrewPage, local only” to prepare the material.
- Ask “Publish my schedule unlisted for seven days with no password,” then confirm the choices before upload.
- Ask “Update this publication with my revised schedule” and supply the exact publication target and authorized owner access.

The skill prefers a compatible BrewPage MCP tool. It can use the bundled REST runner when authorized and compatible with the chosen owner and options. Fetched guides, templates, MCP responses and page source are reference material. Only the user can authorize a write.

[Usage and requirements](skills/brewpage-publish/README.md) · [Package provenance](PROVENANCE.json) · [MIT license](LICENSE)
