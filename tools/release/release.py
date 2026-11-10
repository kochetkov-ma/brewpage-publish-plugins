"""Release tooling for the six AI-agent packages: vendor, build, outputs, reset, assets. Usage: README.md."""
import argparse
import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRS = ('common', 'deepseek', 'kimi', 'mistral', 'qwen', 'yandex')
SEVEN = ['LICENSE', 'README.md', 'SKILL.md', 'scripts/brewpage-lib.sh', 'scripts/brewpage-run.sh', 'scripts/history.py', 'scripts/publish.mjs']
DATE = (2026, 1, 1, 0, 0, 0)
RAW = 'https://raw.githubusercontent.com/kochetkov-ma/claude-brewcode/'
UPSTREAM_DIRECTORY = 'skills/brewpage-publish'
RELEASES = 'https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/tag/'
DEVIATION = 'User-Agent value only: BP_UA line, delete hint, README/SKILL curl examples'
SYNTAX = 'bash -n, node --check, Python parse: pass'
HOSTS = ('qwen', 'deepseek', 'mistral-vibe', 'kimi', 'yandex', 'mistral-work')
# Package key -> (folder of the seven vendored files, renamed members).
VENDORED = {
    'original-skill': ('common/brewpage-publish', {}),
    'mistral-work': ('common/mistral-work/upstream', {}),
    'yandex': ('yandex/brewpage-publish/upstream', {'SKILL.md': 'SKILL.md.source'}),
    'mistral-vibe': ('mistral/brewpage/skills/brewpage-publish/upstream', {}),
    'kimi': ('kimi/brewpage-publish/skills/brewpage-publish', {}),
    'qwen': ('qwen/skills/brewpage-publish/upstream', {}),
    'deepseek': ('deepseek/skills/brewpage-publish/upstream', {}),
}
VERSION_FILES = {
    'qwen': 'qwen/plugin.json',
    'deepseek': 'deepseek/package.json',
    'mistral-vibe': 'mistral/brewpage/plugin.json',
    'kimi': 'kimi/brewpage-publish/kimi.plugin.json',
}
SECRET = re.compile(rb'AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{32,}|xox[abpr]-[A-Za-z0-9-]{10,}'
                    rb'|-----BEGIN [A-Z ]*PRIVATE KEY-----|AIza[0-9A-Za-z_-]{35}')


def fail(message):
    sys.exit('FAILED: ' + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *arguments):
    return subprocess.run(['git', '-C', str(repo), *arguments], check=True, capture_output=True).stdout


def show(repo, ref, path):
    return git(repo, 'show', ref + ':' + path)


def component(path):
    return path.split('/')


def read_config(path):
    cfg = json.loads(Path(path).read_text(encoding='utf-8'))
    if not re.fullmatch(r'[0-9a-f]{40}', cfg['upstream_commit']):
        fail('upstream_commit must be a full 40-character commit hash')
    if sorted(cfg['versions']) != sorted(HOSTS):
        fail('versions must list exactly: ' + ', '.join(HOSTS))
    return cfg


def check_tools(cfg):
    actual = {
        'python': platform.python_version(),
        'zlib': zlib.ZLIB_RUNTIME_VERSION,
        'node': subprocess.run(['node', '--version'], check=True, capture_output=True, text=True).stdout.strip().lstrip('v'),
        'npm': subprocess.run(['npm', '--version'], check=True, capture_output=True, text=True).stdout.strip(),
    }
    if actual != cfg['tools']:
        fail('tool versions differ from the release file: have ' + json.dumps(actual) + ', pinned ' + json.dumps(cfg['tools']))
    print('TOOLS ' + json.dumps(actual))


def user_agent(cfg, key):
    return 'brewpage-' + key + '/' + cfg['versions'][key] + ' (+https://brewpage.app)'


def archives(versions):
    return {
        'qwen': 'qwen/brewpage-qwen-' + versions['qwen'] + '.zip',
        'deepseek': 'deepseek/dsh-brewpage-' + versions['deepseek'] + '.tgz',
        'mistral-vibe': 'mistral/brewpage-vibe-' + versions['mistral-vibe'] + '.zip',
        'kimi': 'kimi/brewpage-kimi-code-' + versions['kimi'] + '.zip',
        'mistral-work': 'common/mistral-work-brewpage-publish-v' + versions['mistral-work'] + '.zip',
        'yandex': 'yandex/yandex-brewpage-publish-v' + versions['yandex'] + '.zip',
        'original-skill': 'common/brewpage-publish.zip',
    }


def previous_versions(cfg, source):
    ref = cfg['baseline']
    previous = {
        'qwen': json.loads(show(source, ref, 'qwen/manifest.json'))['version'],
        'deepseek': json.loads(show(source, ref, 'deepseek/package.json'))['version'],
        'mistral-vibe': json.loads(show(source, ref, 'mistral/manifest.json'))['version'],
        'kimi': json.loads(show(source, ref, 'kimi/brewpage-publish/kimi.plugin.json'))['version'],
        'yandex': json.loads(show(source, ref, 'yandex/manifest.json'))['package_version'],
        'mistral-work': json.loads(show(source, ref, 'common/manifest.json'))['provider_artifacts'][-1]['version'],
    }
    same = [key for key in HOSTS if previous[key] == cfg['versions'][key]]
    if same:
        fail('every package must move to a new version; unchanged since ' + ref + ': ' + ', '.join(same))
    return previous


def outputs(cfg, previous):
    versions = cfg['versions']
    return sorted(list(archives(versions).values()) + [
        'PROVENANCE.json',
        'SHASUMS256.txt',
        'common/manifest.json',
        'deepseek/directory-manifest.json',
        'deepseek/refresh-verification-' + versions['deepseek'] + '.json',
        'kimi/directory-manifest.json',
        'kimi/refresh-verification-' + versions['kimi'] + '.json',
        'kimi/source-hashes.json',
        'mistral/manifest-' + previous['mistral-vibe'] + '.json',
        'mistral/manifest.json',
        'mistral/validation-' + previous['mistral-vibe'] + '.json',
        'mistral/validation.json',
        'qwen/manifest-' + previous['qwen'] + '.json',
        'qwen/manifest.json',
        'qwen/refresh-verification-' + versions['qwen'] + '.json',
        'yandex/manifest.json',
    ])


def upstream(cfg, local):
    commit = cfg['upstream_commit']
    files = {}
    for name in SEVEN:
        request = urllib.request.Request(RAW + commit + '/' + UPSTREAM_DIRECTORY + '/' + name, headers={'User-Agent': 'vendor-check'})
        with urllib.request.urlopen(request, timeout=30) as response:
            files[name] = response.read()
        if local and git(local, 'show', commit + ':' + UPSTREAM_DIRECTORY + '/' + name) != files[name]:
            fail('raw GitHub bytes differ from the local git object: ' + name)
    lines = [line for line in files['scripts/brewpage-lib.sh'].decode().splitlines() if line.startswith('BP_UA=')]
    if len(lines) != 1:
        fail('expected exactly one BP_UA= line upstream')
    return files, lines[0].split('"')[1]


def swapped(data, token, agent):
    if agent is None:
        return data
    result = data.replace(token.encode(), agent.encode())
    if token.split(' ')[0].encode() in result:
        fail('upstream User-Agent product token occurs outside the full User-Agent value')
    return result


def vendored_files(cfg, files, token):
    for key, (directory, rename) in VENDORED.items():
        agent = None if key == 'original-skill' else user_agent(cfg, key)
        for name in SEVEN:
            yield key, name, directory + '/' + rename.get(name, name), swapped(files[name], token, agent)


def zip_bytes(entries, order=None):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries, key=order):
            data, mode = entries[name]
            info = zipfile.ZipInfo(name, DATE)
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            archive.writestr(info, data)
    return buffer.getvalue()


def zip_members(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return {name: sha(archive.read(name)) for name in archive.namelist()}


def tar_members(data):
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        return {member.name: sha(archive.extractfile(member).read()) for member in archive.getmembers() if member.isfile()}


def changed(new, old, strip=''):
    return sorted((name[len(strip):] for name in new if old.get(name) != new[name]), key=component)


def snapshot(source, ref):
    """Complete source zip of a git ref: <name>-<version>/<path>, component-sorted, mode 644, fixed date."""
    version = json.loads(show(source, ref, 'PROVENANCE.json'))['distribution_version']
    paths = [path for path in git(source, 'ls-tree', '-r', '--name-only', ref).decode().split('\n') if path]
    prefix = 'brewpage-publish-plugins-' + version + '/'
    return prefix[:-1] + '.zip', zip_bytes({prefix + path: (show(source, ref, path), 0o100644) for path in paths}, component)


def body_of(text):
    return text[text.index('\n---\n', 4) + 4:]


def vendor(args):
    cfg = read_config(args.config)
    check_tools(cfg)
    files, token = upstream(cfg, args.upstream)
    print('upstream User-Agent: ' + token)
    for key, name, relative, data in vendored_files(cfg, files, token):
        target = args.repo / relative
        if not target.is_file():
            fail('vendored file is missing: ' + relative)
        differs = target.read_bytes() != data
        if differs:
            target.write_bytes(data)
        print(('WROTE ' if differs else 'SAME  ') + sha(data) + '  ' + relative)


def build(args):
    cfg = read_config(args.config)
    repo, source, baseline = args.repo, args.git or args.repo, cfg['baseline']
    commit, versions, notes = cfg['upstream_commit'], cfg['versions'], cfg['notes']
    check_tools(cfg)
    previous = previous_versions(cfg, source)
    new, old_archives = archives(versions), archives(previous)
    agents = {key: user_agent(cfg, key) for key in HOSTS}
    written = []

    def head(path):
        return show(source, baseline, path)

    def fsha(relative):
        return sha((repo / relative).read_bytes())

    def emit(relative, data):
        (repo / relative).write_bytes(data)
        written.append(relative)
        print('WROTE ' + relative)

    def dump(relative, value):
        emit(relative, (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode())

    def tree(root):
        base = repo / root
        names = sorted(path.relative_to(base).as_posix() for path in base.rglob('*') if path.is_file())
        stray = [name for name in names if name.split('/')[-1].startswith('.') or 'node_modules' in name or '__pycache__' in name]
        if stray:
            fail('stray files under ' + root + ': ' + ', '.join(stray))
        return names

    def rows(root, names):
        return [{'path': name, 'sha256': fsha(root + '/' + name)} for name in names]

    def build_zip(target, root, names, prefix):
        entries = {}
        for name in names:
            path = repo / root / name
            entries[prefix + name] = (path.read_bytes(), 0o100755 if os.access(path, os.X_OK) else 0o100644)
        emit(target, zip_bytes(entries))
        with zipfile.ZipFile(repo / target) as archive:
            if archive.testzip() is not None:
                fail('CRC ' + target)
            for name in names:
                if sha(archive.read(prefix + name)) != fsha(root + '/' + name):
                    fail('roundtrip ' + target + ' ' + name)
            if len(archive.namelist()) != len(names):
                fail('entry count ' + target)
        print('BUILT ' + target + ' ' + fsha(target) + ' files=' + str(len(names)))

    def run(label, command, **options):
        result = subprocess.run(command, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', **options}, capture_output=True, text=True)
        if result.returncode != 0:
            fail(label + '\n' + result.stdout + result.stderr)

    for key, path in VERSION_FILES.items():
        if json.loads((repo / path).read_text(encoding='utf-8'))['version'] != versions[key]:
            fail(path + ' version differs from the release file')

    # Source proof: every vendored copy equals raw GitHub at the immutable commit plus the User-Agent swap.
    files, token = upstream(cfg, args.upstream)
    for key, name, relative, data in vendored_files(cfg, files, token):
        if (repo / relative).read_bytes() != data:
            fail('vendored bytes differ from raw GitHub + User-Agent swap: ' + key + ' ' + name)
    print('SOURCE 7 files x 7 packages equal raw GitHub ' + commit + ' (User-Agent swap only); upstream UA ' + token)

    for directory in DIRS:
        for path in sorted((repo / directory).rglob('*')):
            if not path.is_file():
                continue
            if path.suffix == '.sh':
                run('bash -n ' + path.name, ['bash', '-n', str(path)])
            elif path.suffix in ('.mjs', '.js'):
                run('node --check ' + path.name, ['node', '--check', str(path)])
            elif path.suffix == '.py':
                compile(path.read_text(encoding='utf-8'), str(path), 'exec')
            if path.suffix not in ('.zip', '.tgz') and SECRET.search(path.read_bytes()):
                fail('credential pattern in ' + path.relative_to(repo).as_posix())
    print('SYNTAX ' + SYNTAX)
    print('SECRETS embedded credential pattern scan: pass')
    for package in ('qwen', 'deepseek'):
        run(package + '/verify-isolation.py', [sys.executable, str(repo / package / 'verify-isolation.py')])
        print('ISOLATION ' + package + '/verify-isolation.py: pass')
    with tempfile.TemporaryDirectory(prefix='vibe-home-') as vibe:
        home = Path(vibe) / 'vibe'
        run('run.py --check-isolation', [sys.executable, str(repo / 'mistral/brewpage/skills/brewpage-publish/run.py'), '--check-isolation'], VIBE_HOME=str(home))
        state = home / 'brewpage-publish-state'
        if oct(state.stat().st_mode)[-3:] != '700' or oct((state / '.claude/brewpage-history.md').stat().st_mode)[-3:] != '600':
            fail('run.py --check-isolation left wrong permissions')
    print('MISTRAL run.py --check-isolation: pass (0700 state, 0600 history)')

    qwen_files = [row['path'] for row in json.loads(head('qwen/manifest.json'))['files']]
    if sorted(name for name in qwen_files if name.startswith('skills/')) != ['skills/' + name for name in tree('qwen/skills')]:
        fail('qwen file set changed')
    build_zip(new['qwen'], 'qwen', qwen_files, 'qwen/')
    build_zip(new['kimi'], 'kimi/brewpage-publish', tree('kimi/brewpage-publish'), '')
    build_zip(new['mistral-vibe'], 'mistral/brewpage', tree('mistral/brewpage'), 'brewpage/')
    build_zip(new['original-skill'], 'common/brewpage-publish', tree('common/brewpage-publish'), '')
    build_zip(new['mistral-work'], 'common/mistral-work', tree('common/mistral-work'), '')
    build_zip(new['yandex'], 'yandex/brewpage-publish', tree('yandex/brewpage-publish'), 'brewpage-publish/')
    tgz = new['deepseek']
    if not (repo / tgz).is_file():
        fail(tgz + ' is missing: run npm pack --ignore-scripts in deepseek/ first')
    tgz_new = tar_members((repo / tgz).read_bytes())
    for name, digest in tgz_new.items():
        if digest != fsha('deepseek/' + name[len('package/'):]):
            fail('tarball member differs from tree: ' + name)
    print('CHECKED ' + tgz + ' ' + fsha(tgz) + ' files=' + str(len(tgz_new)))

    def receipt(key, artifact, baseline_artifact, members, baseline_members, strip, tests):
        return {
            'version': versions[key],
            'user_agent': agents[key],
            'upstream_commit': commit,
            'upstream_deviation': DEVIATION,
            'artifact': artifact.split('/')[-1],
            'sha256': fsha(artifact),
            'baseline_artifact': baseline_artifact.split('/')[-1],
            'baseline_sha256': sha(head(baseline_artifact)),
            'changed_files': changed(members, baseline_members, strip),
            'file_count': len(members),
            'archive_roundtrip': 'pass',
            'synced_upstream_files': 7,
            'tests': tests,
            'native_import_repeated': False,
            'mcp_execution_repeated': False,
            'live_publish': 'not run',
        }

    def change(key):
        return ('Publishing skill synced to upstream ' + commit[:8] + ' (' + cfg['upstream_label'] + '). ' + notes['change']
                + '. User-Agent version moved to ' + versions[key])

    def isolation(key):
        return 'pass; asserts upload -A == ' + agents[key] + ', ' + notes['isolation_asserts']

    # common/manifest.json: original skill rows plus a new Mistral Work provider entry.
    common = json.loads(head('common/manifest.json'))
    common['source']['commit'] = commit
    common['artifact']['sha256'] = fsha(new['original-skill'])
    common['files'] = rows('common/brewpage-publish', [row['path'] for row in common['files']])
    common['validation']['source_files_refetched_from_immutable_raw_github'] = 7
    common['validation']['source_hashes_match_prior_verified_receipt'] = 7
    common['validation']['zip_roundtrip_files'] = 7
    work_body = body_of((repo / 'common/mistral-work/SKILL.md').read_text(encoding='utf-8'))
    work_body_old = sha(body_of(head('common/mistral-work/SKILL.md').decode()).encode())
    work_files = tree('common/mistral-work')
    work_validation = {
        'zip_crc': 'pass',
        'zip_roundtrip_files': len(work_files),
        'upstream_source_hashes_match': 7,
        'portable_body_sha256': sha(work_body.encode()),
        'portable_body_chars': len(work_body),
    }
    if work_body_old != sha(work_body.encode()):
        work_validation['portable_body_changed_from'] = work_body_old
    work_validation.update({'native_saved_instruction_body_is_separate_surface': True, 'native_import': 'not repeated', 'runtime_publish': 'not run'})
    common['provider_artifacts'].append({
        'provider': 'Mistral Work',
        'version': versions['mistral-work'],
        'folder': 'mistral-work',
        'zip': new['mistral-work'].split('/')[-1],
        'zip_layout': 'SKILL.md at archive root; unchanged source files under upstream/',
        'sha256': fsha(new['mistral-work']),
        'adaptation': notes['mistral_work_adaptation'],
        'files': rows('common/mistral-work', work_files),
        'validation': work_validation,
        'source_commit': commit,
        'user_agent': agents['mistral-work'],
        'upstream_deviation': DEVIATION,
    })
    dump('common/manifest.json', common)

    # qwen: the previous manifest is kept as manifest-<previous>.json.
    old_manifest = head('qwen/manifest.json')
    emit('qwen/manifest-' + previous['qwen'] + '.json', old_manifest)
    old = json.loads(old_manifest)
    qwen_new = zip_members((repo / new['qwen']).read_bytes())
    qwen_receipt = 'refresh-verification-' + versions['qwen'] + '.json'
    dump('qwen/' + qwen_receipt, {
        **receipt('qwen', new['qwen'], old_archives['qwen'], qwen_new, zip_members(head(old_archives['qwen'])), '',
                  {'syntax': SYNTAX, 'verify-isolation.py': isolation('qwen')}),
        'limits': [notes['limit']],
        'change': change('qwen'),
    })
    manifest = dict(old)
    manifest['version'] = versions['qwen']
    manifest['upstream'] = {**old['upstream'], 'commit': commit}
    manifest['artifact'] = {**old['artifact'], 'zip': new['qwen'].split('/')[-1], 'sha256': fsha(new['qwen']), 'file_count': len(qwen_files)}
    manifest['files'] = rows('qwen', qwen_files)
    manifest['validation'] = qwen_receipt
    manifest['historical_artifacts'] = [{'zip': old['artifact']['zip'], 'sha256': old['artifact']['sha256'], 'manifest': 'manifest-' + previous['qwen'] + '.json',
                                         'validation': old['validation']}] + old['historical_artifacts']
    dump('qwen/manifest.json', manifest)

    # deepseek: receipt for the npm tarball and a hash per file of the folder.
    dump('deepseek/refresh-verification-' + versions['deepseek'] + '.json', {
        **receipt('deepseek', tgz, old_archives['deepseek'], tgz_new, tar_members(head(old_archives['deepseek'])), 'package/',
                  {'syntax': SYNTAX, 'verify-isolation.py': isolation('deepseek'), 'verify-native.mjs': notes['deepseek_verify_native']}),
        'limits': [notes['limit']],
        'change': change('deepseek'),
    })
    names = sorted((name for name in tree('deepseek') if name != 'directory-manifest.json'), key=component)
    dump('deepseek/directory-manifest.json', {name: fsha('deepseek/' + name) for name in names})

    # mistral vibe: the previous manifest and validation are kept under their version.
    old_manifest = head('mistral/manifest.json')
    emit('mistral/manifest-' + previous['mistral-vibe'] + '.json', old_manifest)
    emit('mistral/validation-' + previous['mistral-vibe'] + '.json', head('mistral/validation.json'))
    old = json.loads(old_manifest)
    vibe_new = zip_members((repo / new['mistral-vibe']).read_bytes())
    dump('mistral/validation.json', {
        **receipt('mistral-vibe', new['mistral-vibe'], old_archives['mistral-vibe'], vibe_new, zip_members(head(old_archives['mistral-vibe'])), '',
                  {'syntax': SYNTAX, 'run.py --check-isolation': 'pass in a temporary VIBE_HOME (0700 state, 0600 history)'}),
        'limits': [notes['limit']],
        'change': change('mistral-vibe'),
    })
    vibe_files = [row['path'] for row in old['files']]
    if sorted(vibe_files) != tree('mistral/brewpage'):
        fail('mistral file set changed')
    manifest = dict(old)
    manifest['version'] = versions['mistral-vibe']
    manifest['upstream'] = {**old['upstream'], 'commit': commit}
    manifest['artifact'] = {**old['artifact'], 'zip': new['mistral-vibe'].split('/')[-1], 'sha256': fsha(new['mistral-vibe']), 'file_count': len(vibe_files)}
    manifest['files'] = rows('mistral/brewpage', vibe_files)
    manifest['historical_artifacts'] = [{'zip': old['artifact']['zip'], 'sha256': old['artifact']['sha256'], 'manifest': 'manifest-' + previous['mistral-vibe'] + '.json',
                                         'validation': 'validation-' + previous['mistral-vibe'] + '.json'}] + old['historical_artifacts']
    dump('mistral/manifest.json', manifest)

    # kimi: source hashes, receipt, then a hash per file of the folder.
    kimi_new = zip_members((repo / new['kimi']).read_bytes())
    dump('kimi/source-hashes.json', {name: fsha('kimi/brewpage-publish/skills/brewpage-publish/' + name) for name in json.loads(head('kimi/source-hashes.json'))})
    dump('kimi/refresh-verification-' + versions['kimi'] + '.json', {
        **receipt('kimi', new['kimi'], old_archives['kimi'], kimi_new, zip_members(head(old_archives['kimi'])), '', {'syntax': SYNTAX, **notes['kimi_tests']}),
        'note': notes['kimi_note'],
        'limits': [notes['limit']] + notes['kimi_limits'],
    })
    names = sorted((name for name in tree('kimi') if name != 'directory-manifest.json'), key=component)
    dump('kimi/directory-manifest.json', {name: fsha('kimi/' + name) for name in names})

    # yandex: its portable body must equal the Mistral Work body.
    old = json.loads(head('yandex/manifest.json'))
    yandex_body = body_of((repo / 'yandex/brewpage-publish/SKILL.md').read_text(encoding='utf-8'))
    if yandex_body != work_body:
        fail('yandex and mistral-work portable bodies differ')
    manifest = dict(old)
    manifest['package_version'] = versions['yandex']
    manifest['source'] = {**old['source'], 'commit': commit}
    manifest['artifact'] = {**old['artifact'], 'zip': new['yandex'].split('/')[-1], 'sha256': fsha(new['yandex'])}
    manifest['active_manifest'] = {**old['active_manifest'], 'sha256': fsha('yandex/brewpage-publish/SKILL.md'), 'portable_body_sha256': sha(yandex_body.encode())}
    manifest['upstream_files'] = [{**row, 'sha256': fsha('yandex/' + row['archive_path'])} for row in old['upstream_files']]
    manifest['validation'] = {**old['validation'], 'native_import': notes['yandex_native_import']}
    manifest['historical_artifacts'] = [{'zip': old['artifact']['zip'], 'sha256': old['artifact']['sha256'], 'source_commit': old['source']['commit'],
                                         'same_bytes_as_native_imported_archive': old['artifact']['same_bytes_as_native_imported_archive']}] + old['historical_artifacts']
    dump('yandex/manifest.json', manifest)

    # PROVENANCE.json and SHASUMS256.txt: every file of the six folders, then the release assets.
    prov = json.loads(head('PROVENANCE.json'))
    old_inventory = prov['source_inventory_sha256']
    paths = sorted((directory + '/' + name for directory in DIRS for name in tree(directory)), key=component)
    prov['upstream_commit'] = commit
    prov['distribution_version'] = cfg['distribution_version']
    prov['files'] = [{'path': path, 'sha256': fsha(path)} for path in paths]
    prov['source_inventory_sha256'] = sha(''.join(row['sha256'] + '  ' + row['path'] + '\n' for row in prov['files']).encode())
    assets = [(new['qwen'], len(qwen_new)), (tgz, len(tgz_new)), (new['mistral-vibe'], len(vibe_new)), (new['kimi'], len(kimi_new)),
              (new['mistral-work'], len(work_files)), (new['yandex'], len(tree('yandex/brewpage-publish'))), (new['original-skill'], 7)]
    prov['release_assets'] = [{'path': path, 'name': path.split('/')[-1], 'sha256': fsha(path), 'bytes': (repo / path).stat().st_size, 'archive_files': count}
                              for path, count in assets]
    prov['limits'] = prov['limits'][:3] + ['Original seven-file skill is byte-identical to upstream ' + commit[:8] + '; host packages deviate only in the User-Agent value.']
    prov['baseline_release'] = {'url': RELEASES + baseline, 'source_archive_sha256': sha(snapshot(source, baseline)[1]), 'source_inventory_sha256': old_inventory}
    verification = [('qwen/' + qwen_receipt, 'qwen-' + qwen_receipt),
                    ('deepseek/refresh-verification-' + versions['deepseek'] + '.json', 'deepseek-refresh-verification-' + versions['deepseek'] + '.json'),
                    ('kimi/refresh-verification-' + versions['kimi'] + '.json', 'kimi-refresh-verification-' + versions['kimi'] + '.json'),
                    ('mistral/validation.json', 'mistral-vibe-validation-' + versions['mistral-vibe'] + '.json')]
    prov['verification_assets'] = [{'path': path, 'name': name, 'sha256': fsha(path)} for path, name in verification]
    prov['user_agents'] = {**agents, 'original-skill': token}
    dump('PROVENANCE.json', prov)
    lines = [row['sha256'] + '  ' + row['name'] for row in prov['release_assets'] + prov['verification_assets']]
    emit('SHASUMS256.txt', ('\n'.join(lines) + '\n').encode())
    if sorted(written + [tgz]) != outputs(cfg, previous):
        fail('written files differ from the declared outputs')
    print('inventory ' + prov['source_inventory_sha256'] + ' files=' + str(len(paths)))


def list_outputs(args):
    cfg = read_config(args.config)
    vendored = [directory + '/' + rename.get(name, name) for directory, rename in VENDORED.values() for name in SEVEN]
    print('\n'.join(sorted(outputs(cfg, previous_versions(cfg, args.git or args.repo)) + vendored)))


def reset(args):
    """Check trees only: drop generated files and put baseline bytes into the vendored ones."""
    cfg = read_config(args.config)
    if (args.repo / '.git').exists() or not args.git:
        fail('reset works on an exported tree outside git and needs --git for the baseline')
    for relative in outputs(cfg, previous_versions(cfg, args.git)):
        (args.repo / relative).unlink()
    for directory, rename in VENDORED.values():
        for name in SEVEN:
            relative = directory + '/' + rename.get(name, name)
            (args.repo / relative).write_bytes(show(args.git, cfg['baseline'], relative))
    print('RESET generated files removed, vendored files at ' + cfg['baseline'])


def assets(args):
    """Check PROVENANCE.json against a git ref and write that ref's release assets into a new directory."""
    source, ref = args.git or args.repo, args.ref
    prov = json.loads(show(source, ref, 'PROVENANCE.json'))
    tracked = [path for path in git(source, 'ls-tree', '-r', '--name-only', ref, *DIRS).decode().split('\n') if path]
    listed = [row['path'] for row in prov['files']]
    bad = [row['path'] for row in prov['files'] if sha(show(source, ref, row['path'])) != row['sha256']]
    inventory = sha(''.join(row['sha256'] + '  ' + row['path'] + '\n' for row in prov['files']).encode())
    if bad or inventory != prov['source_inventory_sha256'] or listed != sorted(tracked, key=component):
        fail('PROVENANCE.json does not match ' + ref + ': ' + ', '.join(bad))
    args.out.mkdir(parents=True, exist_ok=False)
    for row in prov['release_assets'] + prov['verification_assets']:
        data = show(source, ref, row['path'])
        if sha(data) != row['sha256'] or ('bytes' in row and len(data) != row['bytes']):
            fail('asset row differs from the ref: ' + row['path'])
        (args.out / row['name']).write_bytes(data)
    (args.out / 'PROVENANCE.json').write_bytes(show(source, ref, 'PROVENANCE.json'))
    (args.out / 'SHASUMS256.txt').write_bytes(show(source, ref, 'SHASUMS256.txt'))
    name, data = snapshot(source, ref)
    (args.out / name).write_bytes(data)
    print('PROVENANCE rows=' + str(len(listed)) + ' inventory=' + inventory)
    print('SNAPSHOT ' + name + ' ' + sha(data))
    print('ASSETS ' + str(len(list(args.out.iterdir()))) + ' files in ' + str(args.out))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['vendor', 'build', 'outputs', 'reset', 'assets'])
    parser.add_argument('--config', type=Path, help='release file, e.g. tools/release/releases/1.0.5.json')
    parser.add_argument('--repo', type=Path, default=ROOT, help='tree to read and write (default: this checkout)')
    parser.add_argument('--git', type=Path, help='git repository holding the baseline and --ref (default: --repo)')
    parser.add_argument('--upstream', type=Path, help='optional local claude-brewcode clone, compared with raw GitHub')
    parser.add_argument('--ref', help='assets: git ref of the committed release')
    parser.add_argument('--out', type=Path, help='assets: new directory for the release assets')
    args = parser.parse_args()
    if args.command == 'assets' and not (args.ref and args.out):
        parser.error('assets needs --ref and --out')
    if args.command != 'assets' and not args.config:
        parser.error(args.command + ' needs --config')
    {'vendor': vendor, 'build': build, 'outputs': list_outputs, 'reset': reset, 'assets': assets}[args.command](args)


if __name__ == '__main__':
    main()
