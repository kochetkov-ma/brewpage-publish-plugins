# Release tooling for the AI-agent packages

Rebuilds everything a release of the six host packages (`qwen/`, `deepseek/`,
`mistral/`, `kimi/`, `yandex/`, `common/`) derives from the hand-written files:
the vendored publishing skill, the archives, the manifests and receipts,
`PROVENANCE.json` and `SHASUMS256.txt`. The add-on packages `agent-plugin/`,
`integrations/antigravity-plugin/` and `catalogs/buildwithclaude/` have their own
tags and use `addons.py` ([Add-on packages](#add-on-packages)).

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
| `addons.py` | Add-on packages: `refresh`, `catalog`, `zip`, `check` |

## Inputs

One release file per release, `releases/<distribution version>.json`:

| Field | Meaning |
| --- | --- |
| `distribution_version` | Version of the collection, the release tag without `v` |
| `baseline` | Tag of the previous release; old manifests, archives and versions are read from it |
| `upstream_commit` | Full commit hash in `kochetkov-ma/claude-brewcode`; source of `skills/brewpage-publish` |
| `upstream_label` | Upstream version as written in receipts, e.g. `claude-brewcode v6.12.11` |
| `skill_layout` | `recipes` packages the four canonical `references/` files plus the existing entry, guide, license and four helpers; `legacy` (the default for historical releases) packages the original seven files |
| `versions` | New version of each host package; every one must differ from the baseline |
| `catalog_versions` | Optional since 1.0.8: User-Agent version of the code-host catalog copies `gitverse` (`skills/brewpage-publish/`) and `sourcecraft` (`.sourcecraft/skills/brewpage-publish/upstream/`); when present, both folders are vendored, checked and listed in `PROVENANCE.json` |
| `tools` | Exact Python, zlib, Node and npm versions; the scripts refuse to run with others |
| `notes` | Release wording that goes into the receipts and manifests |

`notes.deepseek_verify_native` is the result of the by-hand native check in
`deepseek/README.md` (it installs the Harness from npm); the build records the
text and does not run that check. Everything else the receipts call `pass` is
run by `build`.

Archive bytes depend on the toolchain (zlib output, `zipfile` headers, npm
tarball layout), so `tools` pins it. 1.0.5 was built with Python 3.14.10,
zlib 1.2.12, Node 24.15.0 and npm 11.12.1.

The scripts read the release's skill members from raw GitHub at
`upstream_commit`. `--upstream <clone>` checks the exact local Git tree and
compares the member bytes against it. Use this option for a `recipes` release.

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
   bash tools/release/check.sh tools/release/releases/X.json --ref HEAD --upstream ../claude-brewcode
   ```

5. Push, then write the release assets into a new directory:

   ```bash
   python3 tools/release/release.py assets --ref HEAD --out /tmp/brewpage-plugins-X
   ```

## Generated files: never edit by hand

`python3 tools/release/release.py outputs --config tools/release/releases/X.json`
prints the exact list. In short:

- the configured skill members in each of the seven package folders, plus the two
  code-host catalog folders when `catalog_versions` is set (upstream bytes;
  host packages differ only in the User-Agent value). The SourceCraft
  `SKILL.md` above its `upstream/` is hand-written; `build` checks its
  frontmatter, that every `{{ input }}` is declared, and its User-Agent
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
executable bit from the file mode. Qwen, Mistral Vibe and DeepSeek retain their
baseline host files and take the vendored skill members from the selected layout.

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

## Add-on packages

`agent-plugin/` and `integrations/antigravity-plugin/` vendor the eleven files of
claude-brewcode `openclaw/brewpage-publish` with their own User-Agent;
`catalogs/buildwithclaude/` is `agent-plugin/` plus its own skill edits. Each
`PROVENANCE.json` records the upstream commit, the member manifest (SHA-256 of
`mode<TAB>sha256<TAB>name` lines) and every file digest. Run from a clean `main`;
`V` is the agent-plugin version, `C` the catalog version, `SHA` the full
upstream commit.

1. Edit the version carriers by hand: `version` in `agent-plugin/plugin.json`,
   `agent-plugin/.claude-plugin/plugin.json`, `agent-plugin/.cursor-plugin/plugin.json`
   and `integrations/antigravity-plugin/plugin.json`, and the versions in both READMEs.
2. `python3 tools/release/addons.py refresh --upstream ../claude-brewcode --commit SHA --version V`
   rewrites the vendored files and both `PROVENANCE.json`. It refuses when a
   vendored file differs from its recorded upstream.
3. Commit, push and tag `brewpage-agent-plugin-vV` (lightweight, like the host tags).
4. Edit `version` in `catalogs/buildwithclaude/.claude-plugin/plugin.json` and its
   README, then `python3 tools/release/addons.py catalog --base-ref brewpage-agent-plugin-vV --version C`.
   It three-way merges the catalog skill edits onto that tag, keeps a new upstream
   insertion next to an unchanged catalog line, and stops on any other overlap.
   Commit, push and tag `brewpage-buildwithclaude-plugin-vC`.
5. `python3 tools/release/addons.py zip --ref <tag> --package agent-plugin|buildwithclaude --out DIR`
   writes the release archive; upload it with `gh release create <tag>`.
   Antigravity installs from the checkout and has no archive.

`python3 tools/release/addons.py check --upstream ../claude-brewcode` rebuilds the
published archives of agent-plugin 1.1.1 and 1.1.2 and BuildWithClaude 1.1.2 and
1.1.3 and compares their SHA-256. It then replays the 1.1.2 refresh and the 1.1.3
catalog rebase from their parent commits. Every package file must come out byte
for byte, with the same mode.

## Limits

All six host packages move to a new version in one release and take the same
upstream commit. A release that changes host-owned archive members needs an
explicit update to the member selection in `release.py`.
