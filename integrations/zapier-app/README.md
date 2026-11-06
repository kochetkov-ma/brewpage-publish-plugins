# BrewPage for Zapier

<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/zapier-app.yml"><img height="18" alt="Zapier app CI" src="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/zapier-app.yml/badge.svg"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Publish HTML and Markdown pages, files and JSON documents from a Zap and get back
an HTTPS link. [BrewPage](https://brewpage.app) needs no signup or API key.
Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme).

This is the source of the Zapier Platform CLI integration. It is not yet
registered, pushed or listed in the Zapier App Directory; see
[Publication](#publication).

## Actions

| Action                            | Sends                                                                    | Returns                                                                                                                |
| --------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| **Publish HTML or Markdown Page** | Content, format (HTML or Markdown), optional title, visibility, lifetime | Page URL, ID, title, format, visibility, namespace, expiry, size, owner token, reused-existing flag, notices           |
| **Upload File**                   | A Zapier file, optional file name, visibility, lifetime                  | File URL, ID, file name, content type, visibility, namespace, expiry, size, owner token, reused-existing flag, notices |
| **Create JSON Document**          | Any valid JSON, lifetime; always private                                 | Document URL, ID, namespace, expiry, size, owner token, notices                                                        |

There are no triggers or searches.

- **Visibility**: _Private_ (default) publishes to the `my` namespace: unlisted
  and not indexed, but anyone with the link can open it. _Public_ publishes to
  `public`: listed in the [gallery](https://brewpage.app/galleries) and
  indexable. JSON documents are never listed.
- **Title** is shown in the browser tab when the content has no `<title>` or
  heading, and names the download. BrewPage stores it as the file name, so it
  needs at least 4 characters.
- **Upload File** downloads the Zapier file without BrewPage headers or the
  owner token, then posts it as multipart. An `.html` or `.md` file becomes a
  page.
- Identical content may return the existing publication (`Reused Existing`
  is true) with its original expiry.

## Connection

The connection has one optional **Owner token** field. Leave it blank to publish
anonymously; every publication then returns its own owner token. Paste a token
from an earlier publish, or mint one in a free profile at
[account.brewpage.app](https://account.brewpage.app), to group publications
under one owner. The connection test reads `GET /api/limits` and, for a token,
`GET /api/publications?limit=1`; a revoked or expired token fails the test.
The token is sent only to `brewpage.app` as `X-Owner-Token`.

The returned owner token updates or deletes a publication. It appears in Zap
history; treat it as a secret and keep it out of shared steps.

## Limits

BrewPage is temporary hosting, not permanent storage.

- Lifetime: 1 to 30 days, default 15; up to 90 with a profile owner token.
  Without a profile the API clamps 31-90 to 30 and says so in Notices. Content
  is deleted for good at expiry.
- Size: page 5 MB; file 5 MB (video 20 MB); JSON document 1 MB; request 25 MB.
  Current values: [`/api/limits`](https://brewpage.app/api/limits).
- Writes are rate-limited per IP. A `429` becomes a Zapier throttling error,
  which Zapier retries later; other errors fail the step with the API message.
- Requests send `User-Agent: brewpage-zapier/1.0.0 (+https://brewpage.app)`.

API reference: [llms.txt](https://brewpage.app/llms.txt),
[API guide](https://brewpage.app/api),
[OpenAPI](https://brewpage.app/api/openapi.yaml).

## Development

Node.js 22.23.4 (the Zapier runtime major is 22), npm 10.9.9. Pinned:
`zapier-platform-core` 19.3.0 and `zapier-platform-cli` 19.3.0 (both released
2026-10-30, latest on 2026-11-06), `form-data` 4.0.6, `nock` 15.0.5,
ESLint 10.13.0, Prettier 3.9.10.

```sh
npm ci --ignore-scripts
npm run lint
npm test
npx zapier-platform validate
```

Tests use `createAppTester` with `nock` and block all network access. CLI 19
installs only the `zapier-platform` binary; `zapier` is its deprecated name.
Without a login, `validate` posts the definition to Zapier's public check
endpoint. The runtime dependency tree has no `npm audit` findings; the CLI
development tree carries upstream advisories and is never bundled.

CI: [`zapier-app.yml`](../../.github/workflows/zapier-app.yml) runs lint, tests
and `zapier-platform validate` on every change to this folder.

## Publication

Not done yet: these steps need the owner's Zapier account (Google sign-in as
the BrewPage owner). Run them in this folder:

```sh
npm ci --ignore-scripts
npx zapier-platform login --sso
npx zapier-platform register "BrewPage" \
  --desc "BrewPage is a free hosting service that publishes HTML pages, Markdown, files and JSON as temporary HTTPS links." \
  --url https://brewpage.app --audience global --role employee \
  --category website-app-building --no-subscribe
npx zapier-platform validate
npx zapier-platform push
```

`register` writes `.zapierapprc` (commit it). Then, in the
[developer platform](https://developer.zapier.com):

1. Integration settings: fill the listing texts below, upload the logo, set
   role **Employee or contractor**, intended audience **Public**.
2. Team: add an admin whose address is on `brewpage.app`, for example
   `info@brewpage.app` (check M005).
3. In a Zapier account, build one Zap per action, turn each on and let each
   run successfully at least once; keep them (checks S002, T001). Invite at
   least two more users who run a live Zap (check S001).
4. Run validation again, then **Publishing** > submit for review.

Listing texts:

| Field                   | Value                                                                                                                                         |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                    | BrewPage                                                                                                                                      |
| Description (112 chars) | BrewPage is a free hosting service that publishes HTML pages, Markdown, files and JSON as temporary HTTPS links.                              |
| Homepage URL            | https://brewpage.app                                                                                                                          |
| Category                | `website-app-building` (Website & App Building; alternative `files`)                                                                          |
| Logo                    | [`assets/brewpage-512.png`](assets/brewpage-512.png): 512 x 512 RGBA PNG                                                                      |
| API documentation       | https://brewpage.app/api and https://brewpage.app/api/openapi.yaml                                                                            |
| Support                 | info@brewpage.app                                                                                                                             |
| Review note             | No signup or API key: the connection's owner token is optional. Leave it blank to test; publications are private (`my` namespace) and expire. |

Review requirements read on 2026-11-06 and how this design meets them:

| Requirement                                                                                                                                                                                                                                                             | Design                                                                                            |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Apps that store private data require authentication; data feeds and utilities may skip it ([auth](https://docs.zapier.com/platform/build/auth)). Check A001 needs a connected account ([checks](https://docs.zapier.com/platform/publish/integration-checks-reference)) | Custom auth with one optional owner token, so an account can be connected with or without a token |
| Credentials only in the auth configuration, never in action fields (requirement 5.5, check D001)                                                                                                                                                                        | The owner token lives only in auth; actions have no token or password field                       |
| Title-cased action names, singular nouns, descriptions starting with a verb; sentence-case field labels ([build guidelines](https://docs.zapier.com/platform/publish/integration-build-guidelines))                                                                     | Followed for all three actions                                                                    |
| Return ID, name and link; ISO 8601 dates with offset; static samples matching live keys (D012, D023, D024)                                                                                                                                                              | Mapped outputs with labels; samples mirror the live smoke shapes                                  |
| User-friendly errors, never a success on failure                                                                                                                                                                                                                        | API status and message mapped to plain messages; `429` raises Zapier's throttle error             |
| Description `<Name> is a...`, 40-140 chars, no Zapier mention (6.2, M002); square RGBA PNG logo of at least 256 px (M004)                                                                                                                                               | See listing texts                                                                                 |
| Admin team member on the app's domain (7.2, M005); valid test account for `integration-testing@zapier.com` (7.1)                                                                                                                                                        | Owner step; BrewPage needs no account, an optional free profile can be created for that address   |
| Production HTTPS endpoints only (4.2, 5.4); latest platform version (D027)                                                                                                                                                                                              | Only `https://brewpage.app/api`; core 19.3.0                                                      |

Sources: [publishing requirements](https://docs.zapier.com/platform/publish/integration-publishing-requirements),
[build guidelines](https://docs.zapier.com/platform/publish/integration-build-guidelines),
[validation checks](https://docs.zapier.com/platform/publish/integration-checks-reference),
[authentication](https://docs.zapier.com/platform/build/auth).

## Support

[info@brewpage.app](mailto:info@brewpage.app). MIT; see [LICENSE](LICENSE). The
license covers this integration, not the hosted BrewPage service.

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) · [BrewPage](https://brewpage.app) · [API guide](https://brewpage.app/api) · [MCP server](https://github.com/kochetkov-ma/brewpage-openapi)
