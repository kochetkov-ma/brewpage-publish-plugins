# Release tooling for the AI-agent packages

Rebuilds everything a release of the six host packages (`qwen/`, `deepseek/`,
`mistral/`, `kimi/`, `yandex/`, `common/`) derives from the hand-written files:
the vendored publishing skill, the archives, the manifests and receipts,
`PROVENANCE.json` and `SHASUMS256.txt`. `agent-plugin/` and `integrations/`
are released separately and are not covered.

Release 1.0.5 is the reference: `check.sh` rebuilds it from tag `v1.0.4` plus
upstream commit `48255159` and gets the committed tree and the published
release assets byte for byte.

## Files

| File | Purpose |
| --- | --- |
| `releases/<version>.json` | Inputs of one release |
| `release.py` | `vendor`, `build`, `outputs`, `assets` (and `reset`, used by `check.sh`) |
| `generate.sh` | `vendor`, `npm pack` in `deepseek/`, `build`; writes into the checkout |
| `check.sh` | Rebuilds a committed release in a temp dir and compares; the checkout is only read |

## Inputs

One release file per release, `releases/<distribution version>.json`:

| Field | Meaning |
| --- | --- |
| `distribution_version` | Version of the collection, the release tag without `v` |
| `baseline` | Tag of the previous release; old manifests, archives and versions are read from it |
| `upstream_commit` | Full commit hash in `kochetkov-ma/claude-brewcode`; source of `skills/brewpage-publish` |
| `upstream_label` | Upstream version as written in receipts, e.g. `claude-brewcode v6.12.11` |
| `versions` | New version of each host package; every one must differ from the baseline |
| `tools` | Exact Python, zlib, Node and npm versions; the scripts refuse to run with others |
| `notes` | Release wording that goes into the receipts and manifests |

`notes.deepseek_verify_native` is the result of the by-hand native check in
`deepseek/README.md` (it installs the Harness from npm); the build records the
text and does not run that check. Everything else the receipts call `pass` is
run by `build`.

Archive bytes depend on the toolchain (zlib output, `zipfile` headers, npm
tarball layout), so `tools` pins it. 1.0.5 was built with Python 3.14.10,
zlib 1.2.12, Node 24.15.0 and npm 11.12.1.

The scripts read raw GitHub at `upstream_commit` (seven files) and write only
local files. `--upstream <clone>` additionally compares those bytes with a
local claude-brewcode clone.

## Release sequence

Run from the repository root, on a clean checkout of `main`. `X` is the new
distribution version.

1. Write `tools/release/releases/X.json` (copy the previous one).
2. Edit by hand what the release changes: package versions in
   `qwen/plugin.json`, `deepseek/package.json`, `mistral/brewpage/plugin.json`
   and `kimi/brewpage-publish/kimi.plugin.json`, the host `SKILL.md` adapters,
   `verify-isolation.py`, the package READMEs and the root `README.md`.
3. Generate:

   ```bash
   bash tools/release/generate.sh tools/release/releases/X.json --upstream ../claude-brewcode
   ```

   A second run over its own result changes nothing.

4. Review `git status` and `git diff`, commit, then prove the commit rebuilds:

   ```bash
   bash tools/release/check.sh tools/release/releases/X.json --ref HEAD
   ```

5. Push, then write the release assets into a new directory:

   ```bash
   python3 tools/release/release.py assets --ref HEAD --out /tmp/brewpage-plugins-X
   ```

## Generated files: never edit by hand

`python3 tools/release/release.py outputs --config tools/release/releases/X.json`
prints the exact list. In short:

- the seven vendored files in each of the seven package folders (upstream
  bytes; host packages differ only in the User-Agent value)
- the new archive of every package, `common/brewpage-publish.zip` and the
  DeepSeek npm tarball
- `common/manifest.json`, `qwen/manifest.json`, `mistral/manifest.json`,
  `yandex/manifest.json` and the kept copies `qwen/manifest-<previous>.json`,
  `mistral/manifest-<previous>.json`, `mistral/validation-<previous>.json`
- `qwen/refresh-verification-<v>.json`, `deepseek/refresh-verification-<v>.json`,
  `kimi/refresh-verification-<v>.json`, `mistral/validation.json`
- `deepseek/directory-manifest.json`, `kimi/directory-manifest.json`,
  `kimi/source-hashes.json`
- `PROVENANCE.json`, `SHASUMS256.txt`
- release only, not committed: `brewpage-publish-plugins-<X>.zip`, the source
  snapshot of the release commit, written by `assets`

Archive conventions: deflate, byte-sorted entry names, entry date 2026-01-01,
executable bit from the file mode. The Qwen archive packs the files listed in
the baseline `qwen/manifest.json`.

## Verify

```bash
bash tools/release/check.sh tools/release/releases/1.0.5.json --ref v1.0.5
```

exports the ref twice into a temp dir, removes the generated files from one
copy, resets its vendored files to the baseline, regenerates and runs
`diff -r` on the two trees; then it writes the release assets from the ref and
runs `shasum -a 256 -c SHASUMS256.txt` on them. Any difference fails.

To compare with a published release as well (only with the release tag as
`--ref`: the source snapshot holds every file of the ref, so a later commit
gives a different snapshot):

```bash
gh release download v1.0.5 --repo kochetkov-ma/brewpage-publish-plugins --dir /tmp/published-1.0.5
bash tools/release/check.sh tools/release/releases/1.0.5.json --ref v1.0.5 --assets /tmp/published-1.0.5
```

`build` itself runs the checks the receipts cite: source bytes against raw
GitHub, `bash -n`, `node --check`, Python compile, the credential pattern
scan, archive CRC and roundtrip, the isolation verifiers
`qwen/verify-isolation.py` and `deepseek/verify-isolation.py`, and
`mistral/brewpage/skills/brewpage-publish/run.py --check-isolation`.

## Steps that stay by hand

- DeepSeek native check (`deepseek/README.md`). It needs the new tarball: run
  step 3, run the check against `deepseek/dsh-brewpage-<v>.tgz`, write its
  result into `notes.deepseek_verify_native`, run step 3 again.
- GitHub release: tag `vX` on the release commit, title
  `BrewPage publishing plugins X`, people-facing notes, and every file of the
  `assets` directory uploaded (`gh release create vX <dir>/*`).
- Native catalogs take the new archive by manual re-import: Yandex AI Studio
  (`yandex-brewpage-publish-v<v>.zip`, Agent Core > Skills) and Mistral Work
  (`mistral-work-brewpage-publish-v<v>.zip`).
- The ClawHub listing of the original skill is published from
  `kochetkov-ma/claude-brewcode`, not from this repository.

## Limits

The build covers the release shape of 1.0.5: all six host packages move to a
new version in one release and take the same upstream commit. A release that
moves only some packages, or changes which files a package ships, needs a
change in `release.py` first; the scripts stop instead of guessing.
