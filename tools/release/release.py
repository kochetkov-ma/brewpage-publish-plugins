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
CORE_MEMBERS = ('LICENSE', 'README.md', 'SKILL.md', 'scripts/brewpage-lib.sh', 'scripts/brewpage-run.sh', 'scripts/history.py', 'scripts/publish.mjs')
RECIPE_MEMBERS = ('references/custom-domain.md', 'references/ownership.md', 'references/page-data.md', 'references/publishing.md')
SKILL_LAYOUTS = {'legacy': CORE_MEMBERS, 'recipes': CORE_MEMBERS + RECIPE_MEMBERS}
DATE = (2026, 1, 1, 0, 0, 0)
RAW = 'https://raw.githubusercontent.com/kochetkov-ma/claude-brewcode/'
UPSTREAM_DIRECTORY = 'skills/brewpage-publish'
RELEASES = 'https://github.com/kochetkov-ma/brewpage-publish-plugins/releases/tag/'
DEVIATION = 'User-Agent value only: BP_UA line, delete hint, README/SKILL curl examples'
SYNTAX = 'bash -n, node --check, Python parse: pass'
HOSTS = ('qwen', 'deepseek', 'mistral-vibe', 'kimi', 'yandex', 'mistral-work')
# Package key -> (vendored skill directory, renamed members).
VENDORED = {
    'original-skill': ('common/brewpage-publish', {}),
    'mistral-work': ('common/mistral-work/upstream', {}),
    'yandex': ('yandex/brewpage-publish/upstream', {'SKILL.md': 'SKILL.md.source'}),
    'mistral-vibe': ('mistral/brewpage/skills/brewpage-publish/upstream', {}),
    'kimi': ('kimi/brewpage-publish/skills/brewpage-publish', {}),
    'qwen': ('qwen/skills/brewpage-publish/upstream', {}),
    'deepseek': ('deepseek/skills/brewpage-publish/upstream', {}),
}
# Code-host catalog copies at the repository root; a release opts in with catalog_versions.
CATALOGS = {
    'gitverse': ('skills/brewpage-publish', {}),
    'sourcecraft': ('.sourcecraft/skills/brewpage-publish/upstream', {'SKILL.md': 'SKILL.md.source'}),
}
CATALOG_ROOTS = ('.sourcecraft', 'skills')
SOURCECRAFT_SKILL = '.sourcecraft/skills/brewpage-publish/SKILL.md'
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
    return subprocess.run(['git', '--no-replace-objects', '-C', str(repo), *arguments], check=True, capture_output=True).stdout


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
    if 'catalog_versions' in cfg and sorted(cfg['catalog_versions']) != sorted(CATALOGS):
        fail('catalog_versions must list exactly: ' + ', '.join(CATALOGS))
    if cfg.get('skill_layout', 'legacy') not in SKILL_LAYOUTS:
        fail('skill_layout must be legacy or recipes')
    return cfg


def skill_members(cfg):
    return SKILL_LAYOUTS[cfg.get('skill_layout', 'legacy')]


def catalogs(cfg):
    return {key: CATALOGS[key] for key in cfg.get('catalog_versions', {})}


def vendored_map(cfg):
    return {**VENDORED, **catalogs(cfg)}


def dirs(cfg):
    return DIRS + (CATALOG_ROOTS if catalogs(cfg) else ())


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
    return 'brewpage-' + key + '/' + {**cfg['versions'], **cfg.get('catalog_versions', {})}[key] + ' (+https://brewpage.app)'


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
    members = skill_members(cfg)
    if cfg.get('skill_layout') == 'recipes' and not local:
        fail('recipes layout needs --upstream to verify the pinned source tree')
    if local:
        if git(local, 'rev-parse', '--verify', commit + '^{commit}').decode().strip() != commit:
            fail('upstream_commit does not identify a commit object')
        prefix = UPSTREAM_DIRECTORY + '/'
        tracked = git(local, 'ls-tree', '-rz', commit, '--', UPSTREAM_DIRECTORY).decode().split('\0')[:-1]
        for entry in tracked:
            if entry.split(' ', 1)[0] not in ('100644', '100755'):
                fail('upstream skill member is not a regular file: ' + entry.partition('\t')[2])
        check_members((entry.partition('\t')[2].removeprefix(prefix) for entry in tracked), members, 'upstream skill')
    files = {}
    for name in members:
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


def vendored_paths(cfg):
    for key, (directory, rename) in vendored_map(cfg).items():
        for name in skill_members(cfg):
            yield key, name, directory + '/' + rename.get(name, name)


def vendored_files(cfg, files, token):
    for key, name, relative in vendored_paths(cfg):
        agent = None if key == 'original-skill' else user_agent(cfg, key)
        yield key, name, relative, swapped(files[name], token, agent)


def check_members(actual, expected, label):
    actual, expected = list(actual), set(expected)
    if len(actual) != len(set(actual)) or set(actual) != expected:
        fail(label + ' file set changed: missing=' + repr(sorted(expected - set(actual)))
             + ', extra=' + repr(sorted(set(actual) - expected)))


def package_members(cfg, key, root, baseline):
    directory, rename = VENDORED[key]
    prefix = directory.removeprefix(root + '/') + '/'
    previous = {name for name in baseline if name.startswith(prefix)}
    current = {prefix + rename.get(name, name) for name in skill_members(cfg)}
    if current == previous:
        return baseline
    return sorted((set(baseline) - previous) | current)


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
        names = archive.namelist()
        if len(set(names)) != len(names):
            fail('duplicate ZIP member')
        return {name: sha(archive.read(name)) for name in names}


def tar_members(data):
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = archive.getmembers()
        names = {member.name for member in members}
        if len(names) != len(members) or any(not member.isfile() or not member.name.startswith('package/') for member in members):
            fail('unexpected or duplicate npm tarball member')
        return {member.name: sha(archive.extractfile(member).read()) for member in members}


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


def check_sourcecraft(text, agent):
    """SourceCraft SKILL.md: name, quoted description, metadata.title, typed inputs, every {{ input }} declared."""
    if not text.startswith('---\n'):
        fail('SourceCraft SKILL.md has no frontmatter')
    head_lines = text[4:text.index('\n---\n', 4)].split('\n')
    if head_lines[0] != 'name: brewpage-publish' or not re.fullmatch(r'description: "[^"]+"', head_lines[1]) or head_lines[2] != 'metadata:':
        fail('SourceCraft frontmatter must start with name: brewpage-publish, a quoted description and metadata:')
    if not any(re.fullmatch(r'  title: \S.*', line) for line in head_lines):
        fail('SourceCraft metadata.title is missing')
    declared, start = {}, head_lines.index('  inputs:')
    for line in head_lines[start + 1:]:
        if not line.startswith('    '):
            break
        if re.fullmatch(r'    [a-z_]+:', line):
            current = line.strip()[:-1]
            declared[current] = {}
        elif re.fullmatch(r'      type: .*', line):
            declared[current]['type'] = line.split(': ', 1)[1]
    if not declared or any(value.get('type') not in ('string', 'bool', 'choice') for value in declared.values()):
        fail('SourceCraft inputs need an explicit type of string, bool or choice')
    used = set(re.findall(r'\{\{ ([a-z_]+) \}\}', body_of(text)))
    if used - set(declared) or not used:
        fail('SourceCraft body uses undeclared inputs: ' + ', '.join(sorted(used - set(declared))))
    if agent not in text:
        fail('SourceCraft SKILL.md does not send User-Agent ' + agent)


def vendor(args):
    cfg = read_config(args.config)
    check_tools(cfg)
    files, token = upstream(cfg, args.upstream)
    print('upstream User-Agent: ' + token)
    entries = list(vendored_files(cfg, files, token))
    for key, name, relative, _ in entries:
        target = args.repo / relative
        if target.is_symlink() or any((args.repo / parent).is_symlink() for parent in target.relative_to(args.repo).parents):
            fail('symlink in vendored file path: ' + relative)
        if target.exists() and not target.is_file():
            fail('vendored path is not a regular file: ' + relative)
        if not target.is_file() and key not in CATALOGS and name not in RECIPE_MEMBERS:
            fail('vendored file is missing: ' + relative)
    for key, name, relative, data in entries:
        target = args.repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        differs = not target.is_file() or target.read_bytes() != data
        if differs:
            target.write_bytes(data)
            if key in CATALOGS and name.startswith('scripts/'):
                target.chmod(0o755)
        print(('WROTE ' if differs else 'SAME  ') + sha(data) + '  ' + relative)


def build(args):
    cfg = read_config(args.config)
    repo, source, baseline = args.repo, args.git or args.repo, cfg['baseline']
    commit, versions, notes = cfg['upstream_commit'], cfg['versions'], cfg['notes']
    recipe_layout = cfg.get('skill_layout') == 'recipes'
    members = skill_members(cfg)
    member_count = len(members)
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
        paths = list(base.rglob('*'))
        if base.is_symlink() or any(path.is_symlink() for path in paths):
            fail('symlink under ' + root)
        names = sorted(path.relative_to(base).as_posix() for path in paths if path.is_file())
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
    for key, (directory, rename) in vendored_map(cfg).items():
        check_members(tree(directory), (rename.get(name, name) for name in members), key + ' vendored skill')
    for key, name, relative, data in vendored_files(cfg, files, token):
        if (repo / relative).read_bytes() != data:
            fail('vendored bytes differ from raw GitHub + User-Agent swap: ' + key + ' ' + name)
    print(f'SOURCE {member_count} files x {len(vendored_map(cfg))} packages equal raw GitHub {commit} (User-Agent swap only); upstream UA {token}')

    for directory in dirs(cfg):
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
    isolation_options = ['--recipes'] if recipe_layout else []
    for package in ('qwen', 'deepseek'):
        run(package + '/verify-isolation.py', [sys.executable, str(repo / package / 'verify-isolation.py'), *isolation_options])
        print('ISOLATION ' + package + '/verify-isolation.py: pass')
    with tempfile.TemporaryDirectory(prefix='vibe-home-') as vibe:
        home = Path(vibe) / 'vibe'
        run('run.py --check-isolation', [sys.executable, str(repo / 'mistral/brewpage/skills/brewpage-publish/run.py'), '--check-isolation'], VIBE_HOME=str(home))
        state = home / 'brewpage-publish-state'
        if oct(state.stat().st_mode)[-3:] != '700' or oct((state / '.claude/brewpage-history.md').stat().st_mode)[-3:] != '600':
            fail('run.py --check-isolation left wrong permissions')
    print('MISTRAL run.py --check-isolation: pass (0700 state, 0600 history)')

    qwen_files = package_members(cfg, 'qwen', 'qwen', [row['path'] for row in json.loads(head('qwen/manifest.json'))['files']])
    check_members((name for name in qwen_files if name.startswith('skills/')), ('skills/' + name for name in tree('qwen/skills')), 'qwen')
    build_zip(new['qwen'], 'qwen', qwen_files, 'qwen/')
    build_zip(new['kimi'], 'kimi/brewpage-publish', tree('kimi/brewpage-publish'), '')
    build_zip(new['mistral-vibe'], 'mistral/brewpage', tree('mistral/brewpage'), 'brewpage/')
    build_zip(new['original-skill'], 'common/brewpage-publish', tree('common/brewpage-publish'), '')
    build_zip(new['mistral-work'], 'common/mistral-work', tree('common/mistral-work'), '')
    build_zip(new['yandex'], 'yandex/brewpage-publish', tree('yandex/brewpage-publish'), 'brewpage-publish/')
    vibe_tests = {'syntax': SYNTAX, 'run.py --check-isolation': 'pass in a temporary VIBE_HOME (0700 state, 0600 history)'}
    if recipe_layout:
        with tempfile.TemporaryDirectory(prefix='vibe-package-') as extracted:
            with zipfile.ZipFile(repo / new['mistral-vibe']) as archive:
                archive.extractall(extracted)
            skill = Path(extracted) / 'brewpage/skills/brewpage-publish'
            run('mistral/verify-isolation.py', [sys.executable, str(repo / 'mistral/verify-isolation.py'), '--skill', str(skill)])
        vibe_tests['verify-isolation.py'] = 'pass on extracted archive: protected management output and owner recovery'
        print('MISTRAL emitted archive receipt and recovery: pass')
    tgz = new['deepseek']
    if not (repo / tgz).is_file():
        fail(tgz + ' is missing: run npm pack --ignore-scripts in deepseek/ first')
    tgz_new = tar_members((repo / tgz).read_bytes())
    tgz_previous = tar_members(head(old_archives['deepseek']))
    deepseek_files = package_members(cfg, 'deepseek', 'deepseek', [name.removeprefix('package/') for name in tgz_previous])
    check_members(tgz_new, ('package/' + name for name in deepseek_files), 'deepseek tarball')
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
            'synced_upstream_files': member_count,
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
    common['files'] = rows('common/brewpage-publish', members)
    common['validation']['source_files_refetched_from_immutable_raw_github'] = member_count
    common['validation']['zip_roundtrip_files'] = member_count
    if recipe_layout:
        common['validation'].pop('source_hashes_match_prior_verified_receipt', None)
        common['validation']['source_hashes_match_local_git_object'] = member_count
        common['validation']['compatibility'] = 'Upstream skill metadata preserved; native compatibility requires native verification.'
    else:
        common['validation']['source_hashes_match_prior_verified_receipt'] = member_count
    work_body = body_of((repo / 'common/mistral-work/SKILL.md').read_text(encoding='utf-8'))
    work_body_old = sha(body_of(head('common/mistral-work/SKILL.md').decode()).encode())
    work_files = tree('common/mistral-work')
    work_validation = {
        'zip_crc': 'pass',
        'zip_roundtrip_files': len(work_files),
        'upstream_source_hashes_match': member_count,
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
        **receipt('deepseek', tgz, old_archives['deepseek'], tgz_new, tgz_previous, 'package/',
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
                  vibe_tests),
        'limits': [notes['limit']],
        'change': change('mistral-vibe'),
    })
    vibe_files = package_members(cfg, 'mistral-vibe', 'mistral/brewpage', [row['path'] for row in old['files']])
    check_members(tree('mistral/brewpage'), vibe_files, 'mistral vibe')
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
    kimi_members = members if recipe_layout else json.loads(head('kimi/source-hashes.json'))
    dump('kimi/source-hashes.json', {name: fsha(VENDORED['kimi'][0] + '/' + name) for name in kimi_members})
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
    yandex_dir, yandex_renames = VENDORED['yandex']
    manifest['upstream_files'] = []
    for name in members:
        path = yandex_dir + '/' + yandex_renames.get(name, name)
        manifest['upstream_files'].append({'original_path': name, 'archive_path': path.removeprefix('yandex/'), 'sha256': fsha(path)})
    manifest['validation'] = {**old['validation'], 'native_import': notes['yandex_native_import']}
    yandex_count = len(tree('yandex/brewpage-publish'))
    if recipe_layout:
        manifest['artifact']['layout'] = f'one top-level folder; one active SKILL.md; {yandex_count} files'
        manifest['validation'].pop('native_mcp_discovery_tools', None)
        manifest['validation'].update(archive_roundtrip_files=yandex_count, upstream_hashes_match=member_count)
    manifest['historical_artifacts'] = [{'zip': old['artifact']['zip'], 'sha256': old['artifact']['sha256'], 'source_commit': old['source']['commit'],
                                         'same_bytes_as_native_imported_archive': old['artifact']['same_bytes_as_native_imported_archive']}] + old['historical_artifacts']
    dump('yandex/manifest.json', manifest)

    if 'sourcecraft' in catalogs(cfg):
        if tree('.sourcecraft') != sorted(['skills/brewpage-publish/SKILL.md'] + ['skills/brewpage-publish/upstream/' + name for name in tree(CATALOGS['sourcecraft'][0])]):
            fail('stray files under .sourcecraft')
        check_sourcecraft((repo / SOURCECRAFT_SKILL).read_text(encoding='utf-8'), user_agent(cfg, 'sourcecraft'))
        print('SOURCECRAFT ' + SOURCECRAFT_SKILL + ': frontmatter, inputs and User-Agent pass')

    # PROVENANCE.json and SHASUMS256.txt: every file of the six folders, then the release assets.
    prov = json.loads(head('PROVENANCE.json'))
    old_inventory = prov['source_inventory_sha256']
    paths = sorted((directory + '/' + name for directory in dirs(cfg) for name in tree(directory)), key=component)
    prov['upstream_commit'] = commit
    prov['distribution_version'] = cfg['distribution_version']
    prov['files'] = [{'path': path, 'sha256': fsha(path)} for path in paths]
    prov['source_inventory_sha256'] = sha(''.join(row['sha256'] + '  ' + row['path'] + '\n' for row in prov['files']).encode())
    assets = [(new['qwen'], len(qwen_new)), (tgz, len(tgz_new)), (new['mistral-vibe'], len(vibe_new)), (new['kimi'], len(kimi_new)),
              (new['mistral-work'], len(work_files)), (new['yandex'], yandex_count), (new['original-skill'], member_count)]
    prov['release_assets'] = [{'path': path, 'name': path.split('/')[-1], 'sha256': fsha(path), 'bytes': (repo / path).stat().st_size, 'archive_files': count}
                              for path, count in assets]
    description = 'Original eleven-file skill' if recipe_layout else 'Original seven-file skill'
    prov['limits'] = prov['limits'][:3] + [description + ' is byte-identical to upstream ' + commit[:8] + '; host packages deviate only in the User-Agent value.']
    if recipe_layout:
        prov['upstream_members'] = [{'path': name, 'sha256': sha(files[name])} for name in members]
    prov['baseline_release'] = {'url': RELEASES + baseline, 'source_archive_sha256': sha(snapshot(source, baseline)[1]), 'source_inventory_sha256': old_inventory}
    verification = [('qwen/' + qwen_receipt, 'qwen-' + qwen_receipt),
                    ('deepseek/refresh-verification-' + versions['deepseek'] + '.json', 'deepseek-refresh-verification-' + versions['deepseek'] + '.json'),
                    ('kimi/refresh-verification-' + versions['kimi'] + '.json', 'kimi-refresh-verification-' + versions['kimi'] + '.json'),
                    ('mistral/validation.json', 'mistral-vibe-validation-' + versions['mistral-vibe'] + '.json')]
    prov['verification_assets'] = [{'path': path, 'name': name, 'sha256': fsha(path)} for path, name in verification]
    prov['user_agents'] = {**agents, **{key: user_agent(cfg, key) for key in catalogs(cfg)}, 'original-skill': token}
    dump('PROVENANCE.json', prov)
    lines = [row['sha256'] + '  ' + row['name'] for row in prov['release_assets'] + prov['verification_assets']]
    emit('SHASUMS256.txt', ('\n'.join(lines) + '\n').encode())
    if sorted(written + [tgz]) != outputs(cfg, previous):
        fail('written files differ from the declared outputs')
    print('inventory ' + prov['source_inventory_sha256'] + ' files=' + str(len(paths)))


def list_outputs(args):
    cfg = read_config(args.config)
    vendored = [relative for _, _, relative in vendored_paths(cfg)]
    print('\n'.join(sorted(outputs(cfg, previous_versions(cfg, args.git or args.repo)) + vendored)))


def reset(args):
    """Check trees only: drop generated files and put baseline bytes into the vendored ones."""
    cfg = read_config(args.config)
    if (args.repo / '.git').exists() or not args.git:
        fail('reset works on an exported tree outside git and needs --git for the baseline')
    for relative in outputs(cfg, previous_versions(cfg, args.git)):
        (args.repo / relative).unlink()
    baseline = cfg['baseline']
    tracked = set(git(args.git, 'ls-tree', '-rz', '--name-only', baseline).decode().split('\0'))
    for key, name, relative in vendored_paths(cfg):
        target = args.repo / relative
        if relative in tracked:
            target.write_bytes(show(args.git, baseline, relative))
        elif key in CATALOGS or name in RECIPE_MEMBERS:
            target.unlink()
        else:
            fail('baseline is missing vendored file: ' + relative)
    print('RESET generated files removed, vendored files at ' + cfg['baseline'])


def assets(args):
    """Check PROVENANCE.json against a git ref and write that ref's release assets into a new directory."""
    source, ref = args.git or args.repo, args.ref
    prov = json.loads(show(source, ref, 'PROVENANCE.json'))
    tracked = [path for path in git(source, 'ls-tree', '-r', '--name-only', ref, *DIRS, *CATALOG_ROOTS).decode().split('\n') if path]
    listed = [row['path'] for row in prov['files']]
    bad = [row['path'] for row in prov['files'] if sha(show(source, ref, row['path'])) != row['sha256']]
    inventory = sha(''.join(row['sha256'] + '  ' + row['path'] + '\n' for row in prov['files']).encode())
    if bad or inventory != prov['source_inventory_sha256'] or listed != sorted(tracked, key=component):
        fail('PROVENANCE.json does not match ' + ref + ': ' + ', '.join(bad))
    if 'upstream_members' in prov:
        originals = prov['upstream_members']
        check_members((row['path'] for row in originals), SKILL_LAYOUTS['recipes'], 'provenance upstream skill')
        root = VENDORED['original-skill'][0]
        hashes = {row['path']: row['sha256'] for row in prov['files']}
        if any(hashes.get(root + '/' + row['path']) != row['sha256'] for row in originals):
            fail('provenance upstream hashes differ from the original skill copy')
    args.out.mkdir(parents=True, exist_ok=False)
    for row in prov['release_assets'] + prov['verification_assets']:
        data = show(source, ref, row['path'])
        if sha(data) != row['sha256'] or ('bytes' in row and len(data) != row['bytes']):
            fail('asset row differs from the ref: ' + row['path'])
        if 'archive_files' in row:
            members = tar_members(data) if row['path'].endswith('.tgz') else zip_members(data)
            if len(members) != row['archive_files']:
                fail('asset member count differs from provenance: ' + row['path'])
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
