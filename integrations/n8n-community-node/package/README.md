# BrewPage for n8n

Publish HTML and Markdown reports as temporary HTTPS reader links. No signup,
credentials or API key. This node installs no runtime package or SDK peer.
This package is an unverified self-hosted community node,
separate from the existing BrewPage workflow template.

## Use

On self-hosted n8n, install `n8n-nodes-brewpage@0.1.0` through **Settings →
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
`User-Agent: brewpage-n8n/0.1.0 (+https://brewpage.app)`. Redirects are disabled.
Network errors expose a fixed message without original error causes; there is no
automatic retry, because a timed-out publication may already exist.
Requests time out after 60 seconds and decoded responses are capped at 64 KiB.

## Development

Use the private build workspace one directory above this package, with Node.js
24.15.0 and npm 11.15.0. There run `npm ci --ignore-scripts`, `npm run build`,
`npm run lint`, `npm run format`, `npm test`, `npm run test:provenance`,
`npm run test:native` (Docker).
Native target: n8n 2.44.7,
`n8n-workflow` 2.44.2 for development types only; CLI 0.55.5, TypeScript 5.9.3,
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
qualified. This package uses erased SDK types and ordinary sanitized errors,
so its compiled JavaScript does not import an SDK and installs no SDK dependency.
That removes a plugin-introduced dependency graph; it does not repair an existing
host. The node's input limits do not establish host-wide immunity.

## Publication and provenance

Source: [integrations/n8n-community-node/package](https://github.com/kochetkov-ma/brewpage-publish-plugins/tree/main/integrations/n8n-community-node/package).
The separate manual `n8n-community-node-provenance.yml` workflow builds, tests,
and packs once without OIDC permission. A separate standard public GitHub-hosted
job downloads only that same run's artifact and signs the exact tarball without
installing the development toolchain.
It uses npm 11.15.0's unmodified native provenance generator with real workflow
OIDC identity. This source-exported internal API is hash-checked; its actual CI
execution and native verification are mandatory release gates. No registry
credentials enter CI. The workflow never publishes to npm.

After reviewing the source commit and successful build and sign jobs, download that
run's release artifact. Using npm 11.15.0, verify it before registry publication:

```sh
node scripts/provenance.cjs verify /absolute/path/to/npm release/n8n-nodes-brewpage-0.1.0.tgz release/n8n-nodes-brewpage-0.1.0.sigstore REVIEWED_40_HEX_SHA https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/runs/RUN_ID/attempts/ATTEMPT
```

The npm directory is the ordinary pinned CLI installation, containing its
`package.json`, `bin` and bundled `node_modules`; it is not an auth/config path.
Verification checks exact packed files and metadata, package PURL/SHA-512,
native Sigstore validity, certificate workflow identity/issuer and source/run
binding. It does not repack. Signatures establish origin, not code safety.
Before signature generation, every packed file and the node source must also
match the committed reviewed `release-baseline.json`. Build summaries cannot
override this independent content check.

Verify publisher identity through ordinary local `npm login --auth-type=web`
and `npm whoami`, honoring any required 2FA, then publish those same bytes once:

```sh
npm publish ./release/n8n-nodes-brewpage-0.1.0.tgz --provenance-file=./release/n8n-nodes-brewpage-0.1.0.sigstore --access=public --registry=https://registry.npmjs.org
```

Do not combine `--provenance-file` with `--provenance`, copy local credentials
into CI or repack the artifact. After an uncertain result, read the exact registry
version before retrying. Verify the anonymous download's integrity, registry
attestation and a real native self-hosted registry installation separately.
No package-name reservation, publication or installation is implied by source
availability. The existing workflow template is independent.

The official strict linter requires an `n8n-workflow` wildcard runtime peer.
This type-only package deliberately needs no runtime SDK peer. Its unmodified
catalog result is recorded separately; no wildcard, artificial peer or disabled
check is introduced. Build/runtime success does not mean
that verified/Cloud submission checks pass. The documented unverified npm
installation route is for self-hosted instances; native custom-extension loading
in the isolated test does not prove npm installation or catalog admission.

Official guidance:
[node CLI](https://docs.n8n.io/connect/create-nodes/build-your-node/using-the-n8n-node-tool/),
[verification](https://docs.n8n.io/connect/create-nodes/build-your-node/reference/verification-guidelines/),
[submission](https://docs.n8n.io/connect/create-nodes/deploy-your-node/submit-community-nodes/),
[self-hosted installation](https://docs.n8n.io/integrations/community-nodes/installation-and-management/gui-installation/),
[BrewPage API](https://brewpage.app/api).
