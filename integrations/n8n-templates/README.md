# BrewPage n8n workflow templates

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for
[BrewPage](https://brewpage.app).

## GitHub release digest to a one-day report

[`brewpage-release-digest.json`](brewpage-release-digest.json) collects public
releases from up to five GitHub repositories, filters them by date and prerelease
preference, removes duplicates and builds a readable HTML digest with source links
and short release-note excerpts. After you review a dry-run preview, it publishes
the digest to BrewPage and returns a link that expires after one day.

- 17 nodes: manual trigger, Code, HTTP Request and If nodes plus sticky notes
  that explain each step. No community node is needed.
- Tested by import and execution on n8n 2.44.7.
- One unauthenticated GitHub GET per repository; one BrewPage POST only when
  dry run is off and you have confirmed visibility and write-once publishing.

### Credentials

None. GitHub's public releases API and BrewPage need no account, API key or
n8n credential. The workflow file holds no secrets.

### Import

1. Download `brewpage-release-digest.json`.
2. In n8n open a new workflow, then use **Import from File** (or paste the JSON
   into the canvas).
3. Open **Report inputs** and set `repositories` (`owner/repo`), `title`,
   `lookbackDays`, `includePrereleases` and `maxReleasesPerRepository`.
4. Execute with `dryRun: true` and read **Dry run preview > content**.
   Nothing is published.
5. To publish, set `visibility` to `public` or `unlisted` (anyone with an
   unlisted link can read it), `acknowledgeWriteOnce: true` and `dryRun: false`,
   then execute once.
6. Share only **Reader URL only > url**.

### Limits

- The report expires after one day and cannot be updated or deleted early
  through this workflow: the owner capability is not kept.
- Only the latest 20 releases per repository are checked.
- GitHub rate limits unauthenticated requests; a 403 or 429 stops the run.

MIT; see [LICENSE](../../LICENSE).
