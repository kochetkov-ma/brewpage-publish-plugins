import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def verify(skill):
    version = json.loads((skill.parents[1] / 'plugin.json').read_text())['version']
    with TemporaryDirectory(prefix='brewpage-vibe-isolation-') as directory:
        # GIVEN a clean Vibe profile, foreign history and a synthetic first-owner reply.
        root = Path(directory).resolve()
        home, workspace, commands = (root / name for name in ('home', 'workspace', 'bin'))
        for path in (home, workspace / '.claude', commands):
            path.mkdir(parents=True, mode=0o700)
        foreign = workspace / '.claude/brewpage-history.md'
        foreign.write_bytes(b'SYNTHETIC_FOREIGN_OWNER')
        foreign.chmod(0o600)
        source = workspace / 'fixture.txt'
        source.write_text('Mistral Vibe isolation fixture\n')
        state = home / 'brewpage-publish-state'
        history = state / '.claude/brewpage-history.md'
        recovery = history.with_name('brewpage-recovery.json')
        sabotage, observed, startup_marker = (root / name for name in ('sabotage', 'argv.json', 'startup-called'))
        startup = root / 'startup.sh'
        startup.write_text(f'touch "{startup_marker}"\n')
        response = {
            'link': 'https://brewpage.app/public/fixtureid1', 'ownerToken': 'V' * 32,
            'manageUrl': 'https://brewpage.app/manage/vibe-fixture#k=fixture-key',
            'ownerLink': 'https://brewpage.app/api/files/public/fixtureid1',
            'namespace': 'public', 'type': 'file', 'id': 'fixtureid1', 'result': {'action': 'created'},
        }
        curl = commands / 'curl'
        curl.write_text(f'''#!{sys.executable}
import json
import sys
from pathlib import Path
Path({str(observed)!r}).write_text(json.dumps(sys.argv[1:]))
if Path({str(sabotage)!r}).exists():
    Path({str(history)!r}).unlink()
    Path({str(history)!r}).symlink_to({str(foreign)!r})
sys.stdout.write({json.dumps(response)!r} + ('\\nBP_HTTP_STATUS:201' if '-w' in sys.argv[1:] else ''))
''')
        curl.chmod(0o700)
        env = {'PATH': str(commands) + os.pathsep + os.environ['PATH'], 'HOME': str(home), 'VIBE_HOME': str(home),
               'CLAUDE_PROJECT_DIR': str(workspace), 'CLAUDE_CONFIG_DIR': str(foreign.parent), 'BASH_ENV': str(startup)}

        def run(*args):
            return subprocess.run([sys.executable, str(skill / 'run.py'), *args],
                                  cwd=workspace, env=env, capture_output=True, text=True)

        # WHEN the installed launcher publishes through the fixture transport.
        command = ('publish', 'file', '--ns', 'public', '--password-file', '', '--path', str(source), '--anonymous')
        ordinary = run(*command)
        reader = 'OK ' + response['link'] + '\n'
        assert (ordinary.returncode, ordinary.stdout) == (0, reader + 'OWNER TOKEN SAVED\n'), 'ordinary result must keep owner proof private'
        argv = json.loads(observed.read_text())
        expected_ua = f'brewpage-mistral-vibe/{version} (+https://brewpage.app)'
        assert argv[argv.index('-A') + 1] == expected_ua, 'fixture upload must use the installed manifest version'
        assert stat.S_IMODE(state.stat().st_mode) == 0o700, 'isolated state directory must have mode 0700'
        assert stat.S_IMODE(history.stat().st_mode) == 0o600, 'isolated history must have mode 0600'
        assert history.read_text().count(response['ownerToken']) == 1, 'private history must contain one saved owner capability'
        assert startup_marker.exists() is False, 'the inherited shell startup file must be absent from the helper environment'

        # THEN explicit private delivery names the protected store, and the proof stays in files.
        private = run(*command, '--private-output')
        private_output = reader + 'OWNER TOKEN SAVED\n' + 'OWNER RECEIPT FILE: ' + str(history) + ' (0600)\n'
        assert (private.returncode, private.stdout) == (0, private_output), 'owner-only output must name the verified store'
        assert response['manageUrl'] not in private.stdout + private.stderr and response['ownerToken'] not in private.stdout + private.stderr, 'owner-only output must keep proof in the store'
        assert history.read_text().count(response['manageUrl']) >= 1, 'the private store must keep the management link for the owner'
        sabotage.touch()
        unsaved = run(*command)
        expected = 'NOTICE: publication confirmed; owner history could not be saved securely\nOWNER RECOVERY SAVED\n' + reader
        assert (unsaved.returncode, unsaved.stdout) == (1, expected), 'failed history write must retain the reader result and protect recovery'
        assert response['ownerToken'] not in unsaved.stderr and response['manageUrl'] not in unsaved.stderr, 'recovery proof must stay out of diagnostic output'
        assert stat.S_IMODE(recovery.stat().st_mode) == 0o600, 'the recovery file must have mode 0600'
        readback = run('owner-recovery', '--private-output')
        assert readback.returncode == 0, 'owner recovery must be reachable through the installed launcher'
        assert json.loads(readback.stdout) == {'ownerApi': response['ownerLink'], 'readerUrl': response['link']}, 'owner recovery must report only the exact target and reader link'
        assert response['ownerToken'] not in readback.stdout and response['manageUrl'] not in readback.stdout, 'owner recovery must keep proof in the file'
        receipt = json.loads(recovery.read_text())
        selected = {'readerUrl': response['link'], 'manageUrl': response['manageUrl'],
                    'ownerToken': response['ownerToken'], 'ownerApi': response['ownerLink']}
        assert {key: receipt[key] for key in selected} == selected, 'the protected recovery file must match the actual publication and proof'
        sabotage.unlink()

        # GIVEN declined history WHEN an owner-only receipt directory is chosen THEN proof lands only in its protected file.
        refused = run(*command, '--no-save')
        assert refused.returncode == 1 and 'requires an absolute --receipt-dir' in refused.stdout + refused.stderr, 'declined history needs a protected receipt directory'
        receipts = root / 'receipts'
        receipts.mkdir(mode=0o700)
        for forbidden in (str(workspace / '.claude'), 'receipts'):
            rejected = run(*command, '--no-save', '--receipt-dir', forbidden)
            assert rejected.returncode == 1 and not (forbidden == 'receipts' and (workspace / 'receipts').exists()), 'Claude or relative receipt directories must be refused'
        observed.unlink()
        declined = run(*command, '--no-save', '--receipt-dir', str(receipts))
        assert (declined.returncode, declined.stdout) == (0, 'OWNER RECOVERY SAVED\n' + reader), 'declined history must confirm protected recovery and the reader result'
        assert response['ownerToken'] not in declined.stdout + declined.stderr and response['manageUrl'] not in declined.stdout + declined.stderr, 'declined history must keep proof out of output'
        declined_file = receipts / 'brewpage-recovery.json'
        assert stat.S_IMODE(declined_file.stat().st_mode) == 0o600, 'the declined-history receipt must have mode 0600'
        stored = json.loads(declined_file.read_text())
        assert {key: stored[key] for key in selected} == selected, 'the declined-history receipt must hold the exact proof'
        assert foreign.read_bytes() == b'SYNTHETIC_FOREIGN_OWNER', 'foreign Claude history must remain byte-identical'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skill', type=Path, required=True)
    verify(parser.parse_args().skill.resolve())
