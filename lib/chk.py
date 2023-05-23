#!/usr/bin/env python3

# TODO maybe make this faster
# FIXME build.py does not appear to depend on chk.py.
# shouldn't this happen automatically?

import sys
import re
import os
import subprocess as sp
from pathlib import Path
from tempfile import mkstemp

def eprint(*args, **kwargs):
    return print(*args, **kwargs, file=sys.stderr)

def git_ignored(file):
    return sp.run(['git', 'check-ignore', '--quiet', str(file)]) \
        .returncode == 0

def is_proj_file(file):
    if not file.is_relative_to(Path.cwd()):
        return False
    if not file.is_file():
        return False
    if git_ignored(file):
        return False
    return True


# Mac syscalls: open, openat, open_nocancel
def do_cmd_mac(c):
    # TODO: Use dtrace(1) directly.
    # NOTE: The dtrace family requires root by default. We don't call sudo
    # b/c there are other ways to make dtrace work which users may prefer.
    cmd = ['dtruss'] + c
    r = sp.run(cmd, capture_output=True, check=True)
    files = []
    for line in r.stderr.decode().split('\n'):
        # TODO
        pass


def do_cmd_linux(c):
    inputs, outputs, inouts = [], [], []

    tmpfd, tmpfn = mkstemp(text=True)
    tmpf = os.fdopen(tmpfd)
    cmd = ['strace', '--output='+tmpfn, '--quiet=all', '--follow-forks',
        '--trace=%file'] + c
    sp.run(cmd, check=True)
    for line in tmpf:
        match = re.match('\d+\s+(\w+)\(', line)
        if match is None:
            continue
        name = match.group(1)
        # FIXME: Breaks if filename contains a comma
        args = re.findall("([^,]+)(?:, |\))", line[line.index('(')+1:])

        if name == "open":
            if len(args) < 2:
                continue
            fname = args[0].strip('"')
            flags = args[1]
        elif name in ("openat", "openat2"):
            if len(args) < 3:
                continue
            fname = args[1].strip('"')
            flags = args[2]
        else:
            continue

        file = Path(fname).resolve()
        if not is_proj_file(file):
            continue

        if "O_RDONLY" in flags or "O_EXEC" in flags and file not in inputs:
            if file not in inputs:
                inputs.append(file)
        elif "O_WRONLY" in flags and file not in outputs:
            outputs.append(file)
        elif "O_RDWR" in flags and file not in inouts:
            inouts.append(file)

    tmpf.close()
    # FIXME doesn't always happen
    os.remove(tmpfn)
    return inputs, outputs, inouts


if len(sys.argv) < 6:
    exit("usage: lib/chk.py inputs outputs cmd")

cmd = sys.argv[5:]

if sys.platform == 'linux':
    inputs, outputs, inouts = do_cmd_linux(cmd)
elif sys.platform == 'darwin':
    inputs, outputs, inouts = do_cmd_mac(cmd)
else:
    exit(f"Unsupported platform '{sys.platform}'")

# TODO abstract the below into fn

user_inputs = [Path(f).resolve() for f in sys.argv[1].split(':')]
user_outputs = [Path(f).resolve() for f in sys.argv[2].split(':')]
ignored_inputs = [p for p in sys.argv[3].split(':')]
ignored_outputs = [p for p in sys.argv[4].split(':')]

if ignored_inputs == ['']: ignored_inputs = []
if ignored_outputs == ['']: ignored_outputs = []

missing_inputs = list(filter(lambda f:
    f not in user_inputs
    and not any([f.match(p) for p in ignored_inputs]), inputs))
missing_outputs = list(filter(lambda f:
    f not in user_outputs
    and not any([f.match(p) for p in ignored_outputs]), outputs))
missing_inouts = list(filter(lambda f:
    f not in user_inputs and f not in user_outputs
    and not any([f.match(p) for p in ignored_inputs])
    and not any([f.match(p) for p in ignored_outputs]), inouts))
unused_inputs = list(filter(lambda f:
    f not in inputs and f not in inouts
    and not any([f.match(p) for p in ignored_inputs]), user_inputs))
unused_outputs = list(filter(lambda f:
    f not in outputs and f not in inouts
    and not any([f.match(p) for p in ignored_outputs]), user_outputs))

warnings, errors = [False] * 2

if len(unused_inputs) > 0:
    eprint(f"\n\033[33mWARNING\033[0m: {sys.argv[5]}: Some input files specified in build.py weren't opened:",
        *[f.relative_to(Path.cwd()) for f in unused_inputs], sep='\n')
    warnings = True

if len(unused_outputs) > 0:
    eprint(f"\n\033[33mWARNING\033[0m: {sys.argv[5]}: Some output files specified in build.py weren't opened:",
        *[f.relative_to(Path.cwd()) for f in unused_outputs], sep='\n')
    warnings = True

if len(missing_inputs) > 0:
    eprint(f"\n\033[31mERROR\033[0m: {sys.argv[5]}: Some input files were opened, but aren't specified in build.py:",
        *[f.relative_to(Path.cwd()) for f in missing_inputs], sep='\n')
    errors = True

if len(missing_outputs) > 0:
    eprint(f"\n\033[31mERROR\033[0m: {sys.argv[5]}: Some output files were opened, but aren't specified in build.py:",
        *[f.relative_to(Path.cwd()) for f in missing_outputs], sep='\n')
    errors = True

if len(missing_inouts) > 0:
    eprint(f"\n\033[31mERROR\033[0m: {sys.argv[3]}: Some files were opened for reading and writing (O_RDWR), but aren't specified as inputs or outputs in build.py:",
        *[f.relative_to(Path.cwd()) for f in missing_inouts], sep='\n')
    errors = True

if warnings and not errors:
    print()

if errors:
    exit("")
