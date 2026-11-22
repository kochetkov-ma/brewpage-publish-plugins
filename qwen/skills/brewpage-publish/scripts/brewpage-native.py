#!/usr/bin/env python3
import os
from pathlib import Path
import stat
import sys


TYPED_COMMANDS = {'preflight', 'publish', 'update'}
FILE_OPTIONS = {'--path', '--password-file', '--owner-token-file', '--exclude-file', '--resolution-file', '--receipt-dir'}
SWITCHES = {'--anonymous', '--confirmed', '--external-only', '--no-save', '--private-output'}


def content_path(value, caller=None):
    path = Path(value)
    absolute = Path(os.path.abspath((caller or Path.cwd()) / path))
    for component in (*path.parts, *absolute.parts, *absolute.resolve().parts):
        component = component.casefold()
        if component == '.claude' or component.startswith('.claude-'):
            raise ValueError('Claude configuration and history paths are forbidden')
    return str(absolute)


def translate_paths(args, caller, state):
    command = args[0] if args else ''
    if command == 'probe':
        if len(args) == 2:
            args[1] = content_path(args[1], caller)
        return
    recovery = Path(state) / '.claude/brewpage-recovery.json'
    index = 2 if command in TYPED_COMMANDS else 1
    while index + 1 < len(args):
        flag, value = args[index:index + 2]
        if flag in SWITCHES:
            index += 1
            continue
        if flag in FILE_OPTIONS and value:
            if command == 'owner-store' and flag == '--owner-token-file' and value == str(recovery):
                if recovery.resolve(strict=True) != recovery:
                    raise ValueError('native recovery receipt must be the fixed private file')
            else:
                args[index + 1] = content_path(value, caller)
        index += 2


def private_root():
    home = os.open(content_path(os.path.expanduser('~')), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    current = home
    try:
        for name in ('.qwen', 'brewpage-publish', 'tmp'):
            try:
                os.mkdir(name, 0o700, dir_fd=current)
            except FileExistsError:
                pass
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            info = os.fstat(child)
            if info.st_uid != os.getuid() or info.st_mode & 0o022:
                os.close(child)
                raise ValueError('unsafe native state directory')
            if name in ('brewpage-publish', 'tmp') and stat.S_IMODE(info.st_mode) != 0o700:
                os.close(child)
                raise ValueError('native publishing state directory must have mode 700')
            if current != home:
                os.close(current)
            current = child
        info = os.fstat(current)
        if stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError('native publishing state directory must have mode 700')
        os.fchdir(current)
        temporary = os.getcwd()
        os.chdir('..')
        return os.getcwd(), temporary
    finally:
        if current != home:
            os.close(current)
        os.close(home)


def main():
    args = sys.argv[1:]
    caller = Path.cwd()
    helper = Path(__file__).resolve().parent.parent / 'upstream/scripts/brewpage-run.sh'
    root, temporary = private_root()
    translate_paths(args, caller, root)
    env = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'LC_ALL') if key in os.environ}
    env.update(CLAUDE_PROJECT_DIR=root, PWD=root, TMPDIR=temporary,
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
               GIT_CEILING_DIRECTORIES=str(Path(root).parent))
    os.execvpe('bash', ['bash', str(helper), *args], env)


try:
    main()
except (OSError, RuntimeError, ValueError):
    sys.stderr.write('FAILED: native publishing state or input path is unsafe\n')
    sys.exit(1)
