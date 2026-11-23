"""Add-on packages (agent-plugin, Antigravity, BuildWithClaude): refresh, catalog, zip, check. Usage: README.md."""
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'openclaw/brewpage-publish'
BODY = 'skills/brewpage-publish/'
# Folders vendored from the OpenClaw tree -> User-Agent product.
ADDONS = {'agent-plugin': 'brewpage-agent-plugin', 'integrations/antigravity-plugin': 'brewpage-antigravity'}
CATALOG, CATALOG_BASE = 'catalogs/buildwithclaude', 'agent-plugin'
# Released archive -> (folder, file name prefix, entry name prefix, entry year).
ARCHIVES = {
    'agent-plugin': ('agent-plugin', 'brewpage-agent-plugin', '', 1980),
    'buildwithclaude': (CATALOG, 'brewpage-buildwithclaude-plugin', 'brewpage-buildwithclaude/', 2026),
}
# check: published archives by tag and the release replays that produced 1.1.2/1.1.3.
PUBLISHED = {
    ('agent-plugin', 'brewpage-agent-plugin-v1.1.1'): '89c0d76e258b8e94f98d54174c7e3ecb71a0d9ad42e0ad6ede7318907c95d7ae',
    ('agent-plugin', 'brewpage-agent-plugin-v1.1.2'): 'a7c8791bcd069a419258dd3d803f52c2312873e9dc46fbebe497f6e7afcfd613',
    ('agent-plugin', 'brewpage-agent-plugin-v1.1.3'): '2150e6ab10923d173ce19e9d19b38c9a11461e327c456b4c1999c64c3a9615c2',
    ('agent-plugin', 'brewpage-agent-plugin-v1.1.4'): '020df51f75fc3e7cb3a69431b24c3ffa51ee0f92ff722db5321c6a0f121a5020',
    ('buildwithclaude', 'brewpage-buildwithclaude-plugin-v1.1.2'): 'a40408247ec646219e085c4ef403e1eb459a12fc25ea29625eb4e6f6e8ebc2f8',
    ('buildwithclaude', 'brewpage-buildwithclaude-plugin-v1.1.3'): 'cc46c589a27a2fc78af947f0f484dc4ded4490f30a77ba6d4efed6d3df7c3614',
    ('buildwithclaude', 'brewpage-buildwithclaude-plugin-v1.1.4'): '5f9c52f5a32d085d40052337275a760121b14c79bfffe6aee526db763eab42d9',
    ('buildwithclaude', 'brewpage-buildwithclaude-plugin-v1.1.5'): '6641ade5011e470c16ed110430c48dbbd144af124033c707e68bbfc6b899adad',
}
REFRESH_REPLAY = ('585373a578d70135a86f967270e1da4e3caf8df2', '82c303d1ee5f0324cfebc8f4529f463bbdc0fc16',
                  '94e3d609e3308be34c0696276a20331fb65c26f4', '1.1.2')
CATALOG_REPLAY = ('82c303d1ee5f0324cfebc8f4529f463bbdc0fc16', '58a3e773a6dd322bc94a236532647004069e2397',
                  'brewpage-agent-plugin-v1.1.2', '1.1.3')
TOKEN = b'@@BREWPAGE_USER_AGENT@@'


def fail(message):
    sys.exit('FAILED: ' + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *arguments):
    return subprocess.run(['git', '--no-replace-objects', '-C', str(repo), *arguments], check=True, capture_output=True).stdout


def entries(repo, ref, folder):
    """{relative path: (mode, bytes)} of a Git tree folder; regular files only."""
    result = {}
    for row in git(repo, 'ls-tree', '-rz', ref, '--', folder).split(b'\0'):
        if row:
            meta, path = row.decode().split('\t', 1)
            mode, kind, oid = meta.split()
            if kind != 'blob' or mode not in ('100644', '100755'):
                fail(f'{path} is not a regular file at {ref}')
            result[path.removeprefix(folder + '/')] = (mode, git(repo, 'cat-file', 'blob', oid))
    return result


def manifest(source):
    return sha(''.join(f'{mode}\t{sha(data)}\t{name}\n' for name, (mode, data) in sorted(source.items())).encode())


def user_agent(source):
    lines = [line for line in source['scripts/brewpage-lib.sh'][1].splitlines() if line.startswith(b'BP_UA="')]
    if len(lines) != 1:
        fail('expected one BP_UA line in the OpenClaw runner')
    return lines[0][len(b'BP_UA="'):-1]


def agent(product, version):
    return f'{product}/{version} (+https://brewpage.app)'


def load(path):
    return json.loads(path.read_bytes())


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf8')


def refresh(repo, upstream, commit, version):
    """Vendor the OpenClaw tree at commit into each add-on; current bytes must equal its recorded commit."""
    new = entries(upstream, commit, SOURCE)
    for folder, product in ADDONS.items():
        root = repo / folder
        provenance = load(root / 'PROVENANCE.json')
        old = entries(upstream, provenance['upstream']['commit'], SOURCE)
        if set(old) - set(new):
            fail('OpenClaw members were removed; update the add-on member lists by hand')
        # A member added upstream is vendored as new; it must not exist in the add-on yet.
        added = [BODY + name for name in sorted(set(new) - set(old))]
        if any((root / path).exists() for path in added):
            fail('a newly added OpenClaw member already exists in ' + folder)
        rows = []
        for path in sorted([row['path'] for row in provenance['vendoredFiles']] + added):
            name, target = path.removeprefix(BODY), root / path
            if path not in added and target.read_bytes() != old[name][1].replace(user_agent(old), provenance['userAgent'].encode()):
                fail(f'{folder}/{path} differs from its recorded upstream; fold that edit upstream first')
            mode, raw = new[name]
            content = raw.replace(user_agent(new), agent(product, version).encode())
            target.write_bytes(content)
            target.chmod(int(mode[-3:], 8))
            rows.append({'path': path, 'mode': '0' + mode[-3:], 'upstreamSha256': sha(raw), 'sha256': sha(content)})
        provenance['version'] = version
        provenance['upstream'].update(commit=commit, memberManifestSha256=manifest(new))
        provenance['userAgent'] = agent(product, version)
        provenance['vendoredFiles'] = rows
        save(root / 'PROVENANCE.json', provenance)
        print(f'REFRESHED {folder} {version}: {len(rows)} files')


def merge(ours, base, theirs):
    """Three-way merge; a conflict whose own side is empty takes the incoming insertion, any other fails."""
    with tempfile.TemporaryDirectory() as work:
        paths = [Path(work, name) for name in ('ours', 'base', 'theirs')]
        for path, data in zip(paths, (ours, base, theirs)):
            path.write_bytes(data)
        result = subprocess.run(['git', 'merge-file', '-p', '-L', 'ours', '-L', 'base', '-L', 'theirs', *map(str, paths)],
                                capture_output=True)
    if result.returncode < 0 or result.returncode > 127:
        fail('git merge-file failed')
    merged = re.sub(rb'<<<<<<< ours\n=======\n(.*?)>>>>>>> theirs\n', rb'\1', result.stdout, flags=re.S)
    return None if b'<<<<<<< ours\n' in merged else merged


def catalog(repo, git_dir, base_ref, version):
    """Rebase the BuildWithClaude skill edits onto the agent-plugin release base_ref; carriers are edited by hand first."""
    root, base_root = repo / CATALOG, repo / CATALOG_BASE
    provenance, base_provenance = load(root / 'PROVENANCE.json'), load(base_root / 'PROVENANCE.json')
    commit = git(git_dir, 'rev-parse', base_ref + '^{commit}').decode().strip()
    released = entries(git_dir, commit, CATALOG_BASE)
    for name, (_, data) in released.items():
        if (base_root / name).read_bytes() != data:
            fail(f'{CATALOG_BASE}/{name} differs from {base_ref}; run catalog on the released add-on tree')
    old = entries(git_dir, provenance['base']['commit'], CATALOG_BASE)
    old_agent = json.loads(old['PROVENANCE.json'][1])['userAgent'].encode()
    new_agent = agent(ADDONS[CATALOG_BASE], version).encode()
    # A skill member new in the base is copied as released; it must not exist in the catalog yet.
    added = sorted(name for name in released if name.startswith(BODY) and name not in old)
    if any((root / name).exists() for name in added):
        fail('a newly added base member already exists in ' + CATALOG)
    for name in added:
        mode, data = released[name]
        (root / name).write_bytes(data.replace(base_provenance['userAgent'].encode(), new_agent))
        (root / name).chmod(int(mode[-3:], 8))
    for target in sorted(path for path in (root / BODY).rglob('*') if path.is_file()):
        name = target.relative_to(root).as_posix()
        if name in added:
            continue
        ours = target.read_bytes().replace(provenance['userAgent'].encode(), TOKEN)
        merged = merge(ours, old[name][1].replace(old_agent, TOKEN), released[name][1].replace(base_provenance['userAgent'].encode(), TOKEN))
        if merged is None:
            fail(f'{CATALOG}/{name}: catalog edit overlaps the new base; resolve by hand')
        target.write_bytes(merged.replace(TOKEN, new_agent))
    rows = provenance['files'] + [{'path': name, 'mode': '0' + released[name][0][-3:], 'sha256': ''} for name in added]
    provenance['files'] = sorted(rows, key=lambda row: row['path'])
    provenance['version'] = version
    provenance['base'].update(tag=base_ref, commit=commit)
    provenance['upstream'] = base_provenance['upstream']
    provenance['userAgent'] = agent(ADDONS[CATALOG_BASE], version)
    for row in provenance['files']:
        row['sha256'] = sha((root / row['path']).read_bytes())
    save(root / 'PROVENANCE.json', provenance)
    print(f'REBASED {CATALOG} {version} on {base_ref}')


def archive(git_dir, ref, package):
    """Deterministic release ZIP of a package at ref: byte-sorted names, fixed date, deflate 9, Unix modes."""
    folder, _, prefix, year = ARCHIVES[package]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for name, (mode, data) in sorted(entries(git_dir, ref, folder).items()):
            entry = zipfile.ZipInfo(prefix + name, (year, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = int(mode, 8) << 16
            target.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


def archive_name(git_dir, ref, package):
    folder, name, _, _ = ARCHIVES[package]
    return f'{name}-{json.loads(git(git_dir, "show", f"{ref}:{folder}/PROVENANCE.json"))["version"]}.zip'


def export(git_dir, ref, target):
    with tarfile.open(fileobj=io.BytesIO(git(git_dir, 'archive', ref))) as tree:
        tree.extractall(target, filter='tar')


def overlay(git_dir, ref, target, folder, keep):
    """Copy the hand-edited files of folder at ref (those keep() accepts) into target."""
    for name, (mode, data) in entries(git_dir, ref, folder).items():
        if keep(name):
            path = target / folder / name
            path.write_bytes(data)
            path.chmod(int(mode[-3:], 8))


def same(git_dir, ref, target, folder):
    expected = entries(git_dir, ref, folder)
    actual = {path.relative_to(target / folder).as_posix(): path for path in (target / folder).rglob('*') if path.is_file()}
    differ = sorted(set(expected) ^ set(actual)) + sorted(name for name in set(expected) & set(actual)
                    if actual[name].read_bytes() != expected[name][1] or oct(actual[name].stat().st_mode & 0o777)[2:] != expected[name][0][-3:])
    if differ:
        fail(f'{folder} differs from {ref}: {", ".join(differ)}')


def check(git_dir, upstream):
    """Rebuild the published archives and replay the 1.1.2 refresh and 1.1.3 catalog rebase from their parents."""
    for (package, tag), digest in PUBLISHED.items():
        if sha(archive(git_dir, tag, package)) != digest:
            fail(f'{archive_name(git_dir, tag, package)} does not reproduce from {tag}')
        print(f'ARCHIVE {archive_name(git_dir, tag, package)} reproduces from {tag}')
    parent, result, commit, version = REFRESH_REPLAY
    with tempfile.TemporaryDirectory() as work:
        export(git_dir, parent, Path(work))
        for folder in ADDONS:
            vendored = {row['path'] for row in load(Path(work, folder, 'PROVENANCE.json'))['vendoredFiles']} | {'PROVENANCE.json'}
            overlay(git_dir, result, Path(work), folder, lambda name: name not in vendored)
        refresh(Path(work), upstream, commit, version)
        for folder in ADDONS:
            same(git_dir, result, Path(work), folder)
    print(f'REPLAY refresh {parent[:7]} -> {result[:7]} equal')
    parent, result, base_ref, version = CATALOG_REPLAY
    with tempfile.TemporaryDirectory() as work:
        export(git_dir, parent, Path(work))
        overlay(git_dir, result, Path(work), CATALOG, lambda name: not name.startswith(BODY) and name != 'PROVENANCE.json')
        catalog(Path(work), git_dir, base_ref, version)
        same(git_dir, result, Path(work), CATALOG)
    print(f'REPLAY catalog {parent[:7]} -> {result[:7]} equal')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['refresh', 'catalog', 'zip', 'check'])
    parser.add_argument('--repo', type=Path, default=ROOT, help='working tree to update (default: this checkout)')
    parser.add_argument('--git', type=Path, default=ROOT, help='repository that holds the refs (default: this checkout)')
    parser.add_argument('--upstream', type=Path, help='local claude-brewcode clone (refresh, check)')
    parser.add_argument('--commit', help='full claude-brewcode commit to vendor (refresh)')
    parser.add_argument('--base-ref', help='released agent-plugin tag to rebase onto (catalog)')
    parser.add_argument('--version', help='new package version (refresh, catalog)')
    parser.add_argument('--ref', help='release tag to archive (zip)')
    parser.add_argument('--package', choices=sorted(ARCHIVES), help='archive to build (zip)')
    parser.add_argument('--out', type=Path, help='output directory (zip)')
    args = parser.parse_args()
    need = {'refresh': ('upstream', 'commit', 'version'), 'catalog': ('base_ref', 'version'),
            'zip': ('ref', 'package', 'out'), 'check': ('upstream',)}[args.command]
    missing = [name for name in need if getattr(args, name) is None]
    if missing:
        fail(f'{args.command} needs ' + ', '.join('--' + name.replace('_', '-') for name in missing))
    if args.command == 'refresh':
        if not re.fullmatch(r'[0-9a-f]{40}', args.commit):
            fail('--commit must be a full commit hash')
        refresh(args.repo, args.upstream, args.commit, args.version)
    elif args.command == 'catalog':
        catalog(args.repo, args.git, args.base_ref, args.version)
    elif args.command == 'zip':
        args.out.mkdir(parents=True, exist_ok=True)
        path = args.out / archive_name(args.git, args.ref, args.package)
        path.write_bytes(archive(args.git, args.ref, args.package))
        print(f'WROTE {path} {sha(path.read_bytes())}')
    else:
        check(args.git, args.upstream)
        print('OK add-on archives and replays reproduce')


if __name__ == '__main__':
    main()
