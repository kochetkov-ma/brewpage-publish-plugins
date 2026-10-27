#!/usr/bin/env python3
import os
from pathlib import Path
import stat
import sys


def content_path(value):
    path = Path(value)
    absolute = Path(os.path.abspath(value))
    for component in (*path.parts, *absolute.parts, *absolute.resolve().parts):
        component = component.casefold()
        if component == '.claude' or component.startswith('.claude-'):
            raise ValueError('Claude configuration and history paths are forbidden')
    return str(absolute)


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
    if args[:1] == ['probe'] and len(args) == 2:
        args[1] = content_path(args[1])
    index = 2 if args[:1] == ['publish'] else 1
    while index < len(args) - 1:
        arg = args[index]
        if arg in ('--path', '--password-file') and args[index + 1]:
            args[index + 1] = content_path(args[index + 1])
        index += 1 if arg == '--confirmed' else 2
    helper = Path(__file__).resolve().parent.parent / 'upstream/scripts/brewpage-run.sh'
    root, temporary = private_root()
    env = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'LC_ALL') if key in os.environ}
    env.update(CLAUDE_PROJECT_DIR=root, PWD=root, TMPDIR=temporary,
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
               GIT_CEILING_DIRECTORIES=str(Path(root).parent))
    os.execvpe('bash', ['bash', str(helper), *args], env)


try:
    main()
except (OSError, ValueError):
    sys.stderr.write('FAILED: native publishing state or input path is unsafe\n')
    sys.exit(1)
