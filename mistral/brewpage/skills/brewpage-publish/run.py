#!/usr/bin/env python3
import os
from pathlib import Path
import stat
import subprocess
import sys


def private_directory(path, exact=False):
    try:
        path.mkdir(mode=0o700)
    except FileExistsError:
        pass
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise ValueError('state directory must be owned and not writable by others')
        if exact and stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError('private state directory must have mode 0700')
    finally:
        os.close(fd)


def content_path(value):
    path = Path(value)
    if not path.is_absolute():
        raise ValueError('content and password paths must be absolute')
    for component in (*path.parts, *path.resolve().parts):
        component = component.casefold()
        if component == '.claude' or component.startswith('.claude-'):
            raise ValueError('Claude configuration and history paths are forbidden')


def main():
    arguments = sys.argv[1:]
    if not arguments or arguments[0] not in ('probe', 'limits', 'stage', 'publish', 'cleanup', '--check-isolation'):
        raise ValueError('expected probe, limits, stage, publish, cleanup or --check-isolation')
    if arguments[0] == 'probe':
        if len(arguments) != 2:
            raise ValueError('probe requires one absolute path')
        content_path(arguments[1])
    index = 2 if arguments[0] == 'publish' else 1
    while index < len(arguments) and arguments[0] != 'probe':
        argument = arguments[index]
        if argument in ('--ns', '--ttl', '--entry', '--delivery-mode', '--password-file', '--text', '--run', '--path', '--review-sha256'):
            if index + 1 >= len(arguments):
                raise ValueError('missing path value')
            if argument in ('--path', '--password-file') and arguments[index + 1]:
                content_path(arguments[index + 1])
            index += 2
        else:
            index += 1
    home = Path(os.environ.get('VIBE_HOME', str(Path.home() / '.vibe')))
    if not home.is_absolute():
        raise ValueError('VIBE_HOME must be absolute')
    content_path(str(home))
    private_directory(home)
    state = home / 'brewpage-publish-state'
    private_directory(state, exact=True)
    temporary = state / 'tmp'
    private_directory(temporary, exact=True)
    environment = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'LC_ALL') if key in os.environ}
    environment.update(CLAUDE_PROJECT_DIR=str(state), TMPDIR=str(temporary),
                       GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
                       GIT_CEILING_DIRECTORIES=str(home))
    upstream = Path(__file__).resolve().parent / 'upstream' / 'scripts'
    if arguments == ['--check-isolation']:
        command = ['bash', '-c', 'source "$1"; bp_history_init', 'brewpage-isolation-check', str(upstream / 'brewpage-lib.sh')]
    else:
        command = ['bash', str(upstream / 'brewpage-run.sh'), *arguments]
    result = subprocess.run(command, cwd=state, env=environment)
    if arguments == ['--check-isolation'] and result.returncode == 0:
        print('Isolated history: ' + str(state / '.claude' / 'brewpage-history.md'))
    return result.returncode


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print('FAILED: ' + str(error), file=sys.stderr)
        sys.exit(1)
