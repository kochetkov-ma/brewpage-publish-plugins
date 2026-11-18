import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


def verify(recipes):
    package = Path(__file__).resolve().parent
    adapter = package / 'skills/brewpage-publish/scripts/brewpage-native.py'
    runtime = '.dsh'
    with tempfile.TemporaryDirectory(prefix='brewpage-isolation-') as temporary:
        root = Path(temporary).resolve()
        home, project, commands = [root / name for name in ('home', 'project', 'bin')]
        for directory in (home, project / '.claude', commands):
            directory.mkdir(parents=True, mode=0o700)
        original = project / '.claude/brewpage-history.md'
        original.write_text('SYNTHETIC_CLAUDE_OWNER_CANARY')
        original.chmod(0o600)
        before = hashlib.sha256(original.read_bytes()).hexdigest()
        manage = 'https://example.invalid/manage/native-fixture#k=fixture-key'
        response = {'link': 'https://example.invalid/native-fixture', 'ownerToken': 'SYNTHETIC_NATIVE_OWNER_ONLY', 'manageUrl': manage}
        published = 'OK https://example.invalid/native-fixture\nMANAGE: ' + manage + '\n'
        authority = ('--anonymous',) if recipes else ()
        visibility = 'VISIBILITY: listed in the public gallery\n'
        if recipes:
            manage = 'https://brewpage.app/manage/native-fixture#k=fixture-key'
            response.update(link='https://brewpage.app/public/fixtureid1', ownerToken='S' * 32, manageUrl=manage,
                            id='fixtureid1', namespace='public', type='file',
                            ownerLink='https://brewpage.app/api/files/public/fixtureid1',
                            visibilityNotice='listed in the public gallery')
            published = 'OK ' + response['link'] + '\nOWNER TOKEN SAVED\n' + visibility
        history = home / runtime / 'brewpage-publish/.claude/brewpage-history.md'
        unsafe = root / 'history-unsafe'
        shim = commands / 'curl'
        marker = root / 'curl-called'
        observed = root / 'curl-environment.json'
        arguments = root / 'curl-arguments.json'
        shim.write_text('#!/usr/bin/env python3\nimport json, os\nfrom pathlib import Path\nPath(' + repr(str(marker)) + ').touch()\nPath(' + repr(str(observed)) + ').write_text(json.dumps(dict(os.environ)))\nimport sys\nPath(' + repr(str(arguments)) + ').write_text(json.dumps(sys.argv[1:]))\nif Path(' + repr(str(unsafe)) + ').exists():\n    Path(' + repr(str(history)) + ').unlink()\n    Path(' + repr(str(history)) + ').symlink_to(' + repr(str(original)) + ')\nprint(' + repr(json.dumps(response)) + ')\n')
        shim.chmod(0o700)
        env = dict(os.environ, HOME=str(home), CLAUDE_PROJECT_DIR=str(project), CLAUDE_CONFIG_DIR=str(project / '.claude'),
                   PATH=str(commands) + os.pathsep + os.environ['PATH'])

        def run(*args, extra=None):
            return subprocess.run([sys.executable, str(adapter), *args], cwd=project, env={**env, **(extra or {})}, text=True, capture_output=True)

        # GIVEN existing Claude owner history and relative source/password paths.
        (project / 'input.txt').write_text('native fixture\n')
        (project / 'password.txt').write_text('fixture-password')
        probe = run('probe', 'input.txt')
        assert probe.returncode == 0, 'native probe must succeed'
        assert 'PATH: ' + str(project / 'input.txt') in probe.stdout, 'relative input must resolve before cwd change'
        site = project / 'site'
        site.mkdir()
        (site / 'index.html').write_text('<!doctype html><title>Fixture</title>')
        (site / 'secret.txt').write_text('synthetic archive-review fixture')
        review = run('publish', 'site-dir', '--ns', 'public', '--password-file', '', '--path', 'site')
        assert review.returncode == 2, 'sensitive archive must still require explicit confirmation'
        assert 'REVIEW_SHA256:' in review.stdout, 'archive approval must remain bound to exact bytes'
        assert not (root / 'curl-called').exists(), 'archive review must precede any mocked upload'

        # WHEN native publishing receives only a mocked response without network traffic.
        result = run('publish', 'file', '--ns', 'public', '--password-file', 'password.txt', '--path', 'input.txt', *authority)
        assert result.returncode == 0, 'native publish fixture must succeed: ' + result.stderr
        assert result.stdout == published, 'stdout must match the layout-specific receipt'

        # THEN history stays runtime-private and a saved owner token never reaches output.
        assert hashlib.sha256(original.read_bytes()).hexdigest() == before, 'existing Claude history must remain unchanged'
        assert stat.S_IMODE(history.stat().st_mode) == 0o600, 'native history must have mode 600'
        assert stat.S_IMODE(history.parent.parent.stat().st_mode) == 0o700, 'native state must have mode 700'
        assert history.read_text().count(response['ownerToken']) == 1, 'one new owner capability must reach native history'
        assert 'SYNTHETIC_CLAUDE_OWNER_CANARY' not in history.read_text(), 'Claude history must never be imported'
        assert response['ownerToken'] not in result.stdout + result.stderr, 'a saved owner token must not reach output'
        assert (root / 'curl-called').exists(), 'fixture must exercise real helper response handling'
        argv = json.loads(arguments.read_text())
        version = json.loads((package / 'package.json').read_text())['version']
        assert argv[argv.index('-A') + 1] == 'brewpage-deepseek/' + version + ' (+https://brewpage.app)', 'upload must send the plugin User-Agent'
        assert not (project / '.gitignore').exists(), 'native adapter must not mutate project ignore state'
        startup = root / 'startup.sh'
        startup.write_text('export CLAUDE_PROJECT_DIR=' + repr(str(project)) + '\n')
        inherited = [
            ('BASH_ENV', {'BASH_ENV': str(startup)}),
            ('SHELLOPTS', {'SHELLOPTS': 'xtrace', 'PS4': 'TRACE: '}),
            ('Git context', {'GIT_DIR': str(project / '.git'), 'GIT_WORK_TREE': str(project), 'GIT_CONFIG_GLOBAL': str(startup), 'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.worktree', 'GIT_CONFIG_VALUE_0': str(project)}),
        ]
        for name, extra in inherited:
            marker.unlink()
            saved_before = history.read_text().count(response['ownerToken'])
            result = run('publish', 'file', '--ns', 'public', '--password-file', '', '--path', 'input.txt', *authority, extra=extra)
            assert result.returncode == 0, name + ': actual helper must still publish through mocked transport'
            assert result.stdout == published, name + ': stdout must match the layout-specific receipt'
            assert response['ownerToken'] not in result.stdout + result.stderr, name + ': a saved owner token must not reach output'
            assert marker.exists(), name + ': fixture must exercise actual response handling'
            child = json.loads(observed.read_text())
            assert [key for key in extra if key in child and key != 'GIT_CONFIG_GLOBAL'] == [], name + ': unsafe inherited variables must be absent'
            assert child['GIT_CONFIG_GLOBAL'] == '/dev/null', name + ': global Git configuration must be disabled'
            assert child['GIT_CONFIG_NOSYSTEM'] == '1', name + ': system Git configuration must be disabled'
            assert child['TMPDIR'] == str(history.parent.parent / 'tmp'), name + ': temporary storage must remain runtime-private'
            assert stat.S_IMODE(Path(child['TMPDIR']).stat().st_mode) == 0o700, name + ': temporary directory must have mode 700'
            assert hashlib.sha256(original.read_bytes()).hexdigest() == before, name + ': foreign Claude history must remain unchanged'
            assert history.read_text().count(response['ownerToken']) == saved_before + 1, name + ': new owner capability must reach only native history'
            assert stat.S_IMODE(history.stat().st_mode) == 0o600, name + ': native history must remain mode 600'
            assert stat.S_IMODE(history.parent.parent.stat().st_mode) == 0o700, name + ': native state must remain mode 700'
            assert not (project / '.gitignore').exists(), name + ': caller Git context must not affect native history'
        alias = project / 'neutral.txt'
        alias.symlink_to(original)
        profile = project / '.claude-profile'
        profile.mkdir()
        (profile / 'history.txt').write_text('SYNTHETIC_PROFILE_CANARY')
        profile_alias = project / 'profile-alias.txt'
        profile_alias.symlink_to(profile / 'history.txt')
        assert (sys.platform != 'darwin' or (project / '.CLAUDE/brewpage-history.md').samefile(original)) is True, 'macOS regression requires actual case-insensitive Claude path access'
        assert (sys.platform != 'darwin' or (project / '.ClAuDe-PrOfIlE/history.txt').samefile(profile / 'history.txt')) is True, 'macOS regression requires actual case-insensitive profile path access'
        forbidden = [
            ('literal content', ['publish', 'file', '--ns', 'public', '--password-file', '', '--path', '.claude/brewpage-history.md']),
            ('aliased content', ['publish', 'file', '--ns', 'public', '--password-file', '', '--path', 'neutral.txt']),
            ('profile content', ['publish', 'file', '--ns', 'public', '--password-file', '', '--path', '.claude-profile/history.txt']),
            ('profile alias content', ['publish', 'file', '--ns', 'public', '--password-file', '', '--path', 'profile-alias.txt']),
            ('literal password', ['publish', 'file', '--ns', 'public', '--password-file', '.claude/brewpage-history.md', '--path', 'input.txt']),
            ('aliased password', ['publish', 'file', '--ns', 'public', '--password-file', 'neutral.txt', '--path', 'input.txt']),
            ('literal probe', ['probe', '.claude/brewpage-history.md']),
            ('aliased probe', ['probe', 'neutral.txt']),
            ('alternate-case content', ['publish', 'file', '--ns', 'public', '--password-file', '', '--path', '.CLAUDE/brewpage-history.md']),
            ('alternate-case password', ['publish', 'file', '--ns', 'public', '--password-file', '.CLAUDE/brewpage-history.md', '--path', 'input.txt']),
            ('alternate-case probe', ['probe', '.CLAUDE/brewpage-history.md']),
            ('mixed-case profile content', ['publish', 'file', '--ns', 'public', '--password-file', '', '--path', '.ClAuDe-PrOfIlE/history.txt']),
            ('mixed-case profile password', ['publish', 'file', '--ns', 'public', '--password-file', '.ClAuDe-PrOfIlE/history.txt', '--path', 'input.txt']),
            ('mixed-case profile probe', ['probe', '.ClAuDe-PrOfIlE/history.txt']),
        ]
        marker.unlink()
        native_before = hashlib.sha256(history.read_bytes()).hexdigest()
        for name, arguments in forbidden:
            result = run(*arguments)
            assert result.returncode == 1, name + ': Claude content path must be refused'
            assert not marker.exists(), name + ': rejection must happen before transport'
            assert 'SYNTHETIC_' not in result.stdout + result.stderr, name + ': no owner data may reach output'
            assert hashlib.sha256(original.read_bytes()).hexdigest() == before, name + ': foreign history must remain unchanged'
            assert hashlib.sha256(history.read_bytes()).hexdigest() == native_before, name + ': native history must remain unchanged on path rejection'
            assert stat.S_IMODE(history.stat().st_mode) == 0o600, name + ': native history must remain mode 600'
            assert stat.S_IMODE(history.parent.parent.stat().st_mode) == 0o700, name + ': native state must remain mode 700'
        if recipes:
            # GIVEN an owner-only channel WHEN private output is selected THEN it carries the management link.
            private = run('publish', 'file', '--ns', 'public', '--password-file', '', '--path', 'input.txt',
                          '--private-output', *authority)
            expected = ('OK ' + response['link'] + '\nMANAGE: ' + manage + '\nOWNER TOKEN SAVED\n'
                        + 'OWNER RECEIPT FILE: ' + str(history) + ' (0600)\n' + visibility)
            assert (private.returncode, private.stdout) == (0, expected), 'explicit private delivery must identify the verified store'
            assert response['ownerToken'] not in private.stdout + private.stderr, 'a saved token must remain in the private store'
        # WHEN history becomes unsafe during the upload THEN recover the proof through the selected receipt path.
        unsafe.touch()
        unsaved = run('publish', 'file', '--ns', 'public', '--password-file', '', '--path', 'input.txt', *authority)
        unsafe.unlink()
        assert unsaved.returncode == 1, 'an unsaved owner token must not report success'
        if recipes:
            expected = ('NOTICE: publication confirmed; owner history could not be saved securely\n'
                        + 'OWNER RECOVERY SAVED\nOK ' + response['link'] + '\n' + visibility)
            assert unsaved.stdout == expected, 'ordinary output must confirm publication and omit private recovery details'
            assert manage not in unsaved.stderr and response['ownerToken'] not in unsaved.stderr, 'stderr must omit private proof'
            recovery = history.with_name('brewpage-recovery.json')
            assert stat.S_IMODE(recovery.stat().st_mode) == 0o600, 'recovery must be protected on disk'
            private = run('owner-recovery', '--private-output')
            assert private.returncode == 0, 'the isolated launcher must support explicit private recovery'
            receipt = json.loads(private.stdout)
            keys = ('readerUrl', 'manageUrl', 'ownerToken', 'ownerApi')
            expected_receipt = dict(zip(keys, (response['link'], manage, response['ownerToken'], response['ownerLink'])))
            assert {key: receipt[key] for key in keys} == expected_receipt, 'private recovery must return the exact proof and publication'
        else:
            assert unsaved.stdout == 'FAILED: published but owner token could not be saved securely\nURL: https://example.invalid/native-fixture\nMANAGE: ' + manage + '\nOWNER TOKEN: SYNTHETIC_NATIVE_OWNER_ONLY\n', 'a live page must hand over its link, management link and token when history cannot keep them'
        assert hashlib.sha256(original.read_bytes()).hexdigest() == before, 'unsafe history target must remain unchanged'
        marker.touch()
        (root / 'curl-called').unlink()
        history.unlink()
        history.symlink_to(original)
        rejected = run('publish', 'file', '--ns', 'public', '--password-file', '', '--path', 'input.txt', *authority)
        assert rejected.returncode == 1, 'native history symlink must be refused before upload'
        assert not (root / 'curl-called').exists(), 'unsafe history must prevent upload'
        assert hashlib.sha256(original.read_bytes()).hexdigest() == before, 'symlink target must remain unchanged'
        print('PASS native isolation, BASH_ENV/SHELLOPTS/Git scrub, 14 forbidden path cases including alternate case, archive consent, relative paths, permissions, symlink refusal, management link output, unsaved-token handover; mocked curl only')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--recipes', action='store_true')
    verify(parser.parse_args().recipes)
