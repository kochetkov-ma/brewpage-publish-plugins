# BrewPage for n8n

<a href="https://www.npmjs.com/package/n8n-nodes-brewpage"><img height="18" alt="npm n8n-nodes-brewpage" src="https://img.shields.io/npm/v/n8n-nodes-brewpage?label=n8n-nodes-brewpage"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/n8n-community-node-provenance.yml"><img height="18" alt="n8n node CI" src="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/n8n-community-node-provenance.yml/badge.svg"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for
[BrewPage](https://brewpage.app).

Publish HTML and Markdown reports as temporary HTTPS reader links. No signup,
credentials or API key. The node installs no runtime dependency; its only peer
is `n8n-workflow`, which the n8n host provides. This package is an unverified
self-hosted community node, separate from the existing BrewPage workflow
template.

## Use

On self-hosted n8n, install `n8n-nodes-brewpage@0.1.1` through **Settings →
Community nodes** after npm publication and accept the native unverified-code
notice. Add **BrewPage**, choose **Publish Report**, select HTML or Markdown,
and map Content from a previous node, for example `={{ $json.report }}`.
Choose Access explicitly and set Lifetime from 1 to 30 days (default 15).
Content must be nonempty and at most 5 MiB in UTF-8.
Content, Format and Access expressions must return strings; structured values
are rejected before any request.

- **Unlisted**: anyone with the link can read it. It is not private.
- **Public**: discoverable in the gallery; anyone can read it.
- Content expires permanently. Identical existing content may retain its original
  expiry; check the returned `expiresAt` and `reusedExisting`.
- Output contains only `link`, `access`, `format`, `expiresAt`,
  `requestedTtlDays`, and `reusedExisting`. Owner tokens, management links,
  response bodies and input content are discarded from node output.
- Ownership tokens are deliberately discarded: this node cannot update or delete
  a publication. Do not publish material that needs early deletion.
- Publish only reports intended for sharing. Do not include secrets or personal
  data. This node has no password option.

Before using report inputs, disable workflow execution saving for success,
errors, progress and manual runs, and do not pin data. n8n itself can persist
workflow parameters, input data, execution snapshots and logs. This package
cannot override instance administration, upstream nodes, telemetry or logging;
keep report content out of literal node parameters and persistent upstream data.
Credential/response redaction in this node does not guarantee platform-wide
secrecy.

The only network destination is `https://brewpage.app/api/html`. Requests send
`User-Agent: brewpage-n8n/0.1.1 (+https://brewpage.app)`. Redirects are disabled.
Every failure throws an n8n `NodeOperationError` with one fixed message and no
original error or response; there is no automatic retry, because a timed-out
publication may already exist.
Requests time out after 60 seconds and decoded responses are capped at 64 KiB.

## Development

Use the private build workspace one directory above this package, with Node.js
24.15.0 and npm 11.15.0. There run `npm ci --ignore-scripts`, `npm run build`,
`npm run lint`, `npm run format`, `npm test`, `npm run test:provenance`,
`npm run test:native` (Docker).
Native target: n8n 2.44.7,
`n8n-workflow` 2.44.2 for development (the host supplies it at runtime); CLI 0.55.5, TypeScript 5.9.3,
Prettier 3.9.10. The separate private build root applies the compatible `qs`
6.16.2 patch without any override in this published package.
The official CLI programmatic starter supplies the package/config conventions;
its `new` command also initializes Git, so these files were adapted directly
from its installed templates without mutating Git.

## Host dependency advisory

The tested n8n 2.44.7 host's SDK includes Zod 3.25.76, affected by
[GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5)
(memory exhaustion from oversized constrained collections). The published fix is
Zod 4.6.6; replacing the host's 3.x API with that major version has not been
qualified. The compiled node loads `n8n-workflow` from the host as a peer, for
`NodeOperationError` and `NodeConnectionTypes`, and installs no dependency of its
own. It adds no dependency graph; it does not repair an existing host. The
node's input limits do not establish host-wide immunity.

## Publication and provenance

Source: [integrations/n8n-community-node/package](https://github.com/kochetkov-ma/brewpage-publish-plugins/tree/main/integrations/n8n-community-node/package).
The manual `n8n-community-node-provenance.yml` workflow runs for a reviewed
public main commit. Its build job formats, builds, tests, runs four native
engine fixtures and packs once, without OIDC permission. A separate sign job
downloads only that same run's artifact and signs the exact tarball with npm
11.15.0's unmodified native provenance generator and real workflow OIDC identity.
The catalog job runs the unmodified official `n8n-node lint`, which passes.

With the `publish` input set, a publish job runs only after the sign and catalog
jobs pass. It re-verifies the same-run tarball and bundle, checks that the
version is not yet on the registry, and publishes those bytes once through npm
trusted publishing (GitHub OIDC), attaching the verified bundle. No registry
token is stored in the repository or in CI. The npm package must name this
repository and workflow file as its trusted publisher.

To verify a downloaded release artifact locally with npm 11.15.0:

```sh
node scripts/provenance.cjs verify /absolute/path/to/npm release/n8n-nodes-brewpage-0.1.1.tgz release/n8n-nodes-brewpage-0.1.1.sigstore REVIEWED_40_HEX_SHA https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/runs/RUN_ID/attempts/ATTEMPT
```

The npm directory is the ordinary pinned CLI installation, containing its
`package.json`, `bin` and bundled `node_modules`; it is not an auth/config path.
Verification checks exact packed files and metadata, package PURL/SHA-512,
native Sigstore validity, certificate workflow identity/issuer and source/run
binding. It does not repack. Signatures establish origin, not code safety.
Before signature generation, every packed file and the node source must also
match the committed reviewed `release-baseline.json`. Build summaries cannot
override this independent content check.

After publication, read the exact registry version, verify the anonymous
download's integrity and registry attestation, and test a real self-hosted
registry installation separately. A passing lint does not mean verified or Cloud
admission; the documented unverified npm route is for self-hosted instances.

Official guidance:
[node CLI](https://docs.n8n.io/connect/create-nodes/build-your-node/using-the-n8n-node-tool/),
[verification](https://docs.n8n.io/connect/create-nodes/build-your-node/reference/verification-guidelines/),
[submission](https://docs.n8n.io/connect/create-nodes/deploy-your-node/submit-community-nodes/),
[self-hosted installation](https://docs.n8n.io/integrations/community-nodes/installation-and-management/gui-installation/),
[BrewPage API](https://brewpage.app/api).

## Related

[All BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) ·
[BrewPage](https://brewpage.app) ·
[MCP server](https://github.com/kochetkov-ma/brewpage-openapi) ·
[Cookbook](https://github.com/kochetkov-ma/brewpage-cookbook)
