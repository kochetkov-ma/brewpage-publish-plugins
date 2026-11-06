# BrewPage n8n build workspace

<a href="https://www.npmjs.com/package/n8n-nodes-brewpage"><img height="18" alt="npm n8n-nodes-brewpage" src="https://img.shields.io/npm/v/n8n-nodes-brewpage?label=n8n-nodes-brewpage"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/n8n-community-node-provenance.yml"><img height="18" alt="n8n node CI" src="https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/workflows/n8n-community-node-provenance.yml/badge.svg"></a>
<a href="https://github.com/kochetkov-ma/brewpage-publish-plugins/blob/main/LICENSE"><img height="18" alt="license MIT" src="https://img.shields.io/badge/license-MIT-green"></a>

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for
[BrewPage](https://brewpage.app).

The [published node source](package/README.md) is in `package/`. This private build
root is never published. It isolates the development SDK/CLI and the compatible
`qs` 6.16.2 override from the dependency-free community package.

Use Node 24.15.0 and npm 11.15.0 in this directory:

```sh
npm ci --ignore-scripts
npm run format
npm run build
npm test
npm run test:provenance
npm run test:native
npm run lint
```

The exact development SDK is 2.44.2; the native fixture engine is n8n 2.44.7.
The published package has no runtime dependency; its one peer, `n8n-workflow`
(`*`), comes from the n8n host. This avoids plugin-introduced SDK installation,
not vulnerabilities in an existing n8n host.
The private development graph still contains documented upstream advisories;
its fixed-source build job has no OIDC permission or registry credentials.

`package/release-baseline.json` freezes the reviewed seven packed-file hashes and
node source hash. A source/package change requires fresh build, tests, pack
inspection and baseline review. The signer verifies those committed hashes before
calling npm's native generator; it never trusts an unsigned build summary alone.
It also compares the full original tarball/subject/file tuple with the build's
pack manifest and exact successful check receipt before signing. This preserves
the pack-once bytes; the unsigned receipt does not add authenticity to the baseline.

Run the manual provenance workflow only for a reviewed public main commit. Its
catalog job runs the unmodified official lint. With `publish: true` it then
publishes the same-run signed tarball through npm trusted publishing; see the
package's [publication notes](package/README.md#publication-and-provenance).
A release bumps the version in `package/package.json`, the node User-Agent,
`scripts/provenance.cjs`, the tests and the workflow `RELEASE`, then refreshes
`package/release-baseline.json` from a fresh pack.

Related: [all BrewPage integrations](https://github.com/kochetkov-ma/brewpage-publish-plugins#integrations) ·
[BrewPage](https://brewpage.app).
