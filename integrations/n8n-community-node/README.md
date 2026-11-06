# BrewPage n8n build workspace

Part of [BrewPage publishing plugins](../../README.md) for
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

The exact typing SDK is 2.44.2; the native fixture engine is n8n 2.44.7. The
published JavaScript has no SDK import or runtime dependency/peer. This removes
plugin-introduced SDK installation, not vulnerabilities in an existing n8n host.
The private development graph still contains documented upstream advisories;
its fixed-source build job has no OIDC permission or registry credentials.

`package/release-baseline.json` freezes the reviewed seven packed-file hashes and
node source hash. A source/package change requires fresh build, tests, pack
inspection and baseline review. The signer verifies those committed hashes before
calling npm's native generator; it never trusts an unsigned build summary alone.
It also compares the full original tarball/subject/file tuple with the build's
pack manifest and exact successful check receipt before signing. This preserves
the pack-once bytes; the unsigned receipt does not add authenticity to the baseline.

Run the manual provenance workflow only for a reviewed public main commit. It
never publishes to npm. Download only the signed artifact after its build and
sign jobs pass, then follow the package's local publication instructions.
Catalog qualification remains a separate unmodified official check.
