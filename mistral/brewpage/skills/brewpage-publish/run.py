#!/usr/bin/env python3
import os
from pathlib import Path
import stat
import subprocess
import sys


TYPED_COMMANDS = {'preflight', 'publish', 'update'}
COMMANDS = TYPED_COMMANDS | {'probe', 'limits', 'stage', 'cleanup', 'owner-store', 'owner-recovery', 'owner-pending', 'owner-reconcile', '--check-isolation'}
FILE_OPTIONS = {'--path', '--password-file', '--owner-token-file', '--exclude-file', '--resolution-file'}
SWITCHES = {'--anonymous', '--confirmed', '--external-only', '--no-save', '--private-output'}


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
        raise ValueError('input and protected file paths must be absolute')
    for component in (*path.parts, *path.resolve().parts):
        component = component.casefold()
        if component == '.claude' or component.startswith('.claude-'):
            raise ValueError('Claude configuration and history paths are forbidden')


def check_paths(arguments, state):
    command = arguments[0]
    if command == 'probe':
        if len(arguments) != 2:
            raise ValueError('probe requires one absolute path')
        content_path(arguments[1])
        return
    recovery = state / '.claude/brewpage-recovery.json'
    index = 2 if command in TYPED_COMMANDS else 1
    while index + 1 < len(arguments):
        flag, value = arguments[index:index + 2]
        if flag in SWITCHES:
            index += 1
            continue
        if flag in FILE_OPTIONS and value:
            if command == 'owner-store' and flag == '--owner-token-file' and value == str(recovery):
                if recovery.resolve(strict=True) != recovery:
                    raise ValueError('native recovery receipt must be the fixed private file')
            else:
                content_path(value)
        index += 2


def main():
    arguments = sys.argv[1:]
    if not arguments or arguments[0] not in COMMANDS:
        raise ValueError('unsupported BrewPage runner command')
    home = Path(os.environ.get('VIBE_HOME', str(Path.home() / '.vibe')))
    if not home.is_absolute():
        raise ValueError('VIBE_HOME must be absolute')
    content_path(str(home))
    private_directory(home)
    home = home.resolve()
    state = home / 'brewpage-publish-state'
    check_paths(arguments, state)
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
    except ValueError as error:
        print('FAILED: ' + str(error), file=sys.stderr)
        sys.exit(1)
    except (OSError, RuntimeError):
        print('FAILED: native publishing state or input path is unsafe', file=sys.stderr)
        sys.exit(1)
