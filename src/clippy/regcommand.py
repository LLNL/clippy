# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT
''' Utilities for querying and creating registered commands.'''

from __future__ import annotations

import pathlib
import json
import logging
import os
import subprocess
from clippy.error import ClippyConfigurationError
from clippy.ooclippy import process_member_function
from clippy.anydict import AnyDict
from clippy.version import _check_version


CLIPPY_ENV = 'CLIPPY_ENV'
CLIPPY_CFG = '.clippy'
JSON_FLAG = '--clippy-help'


def _is_exe(f: pathlib.Path):
    '''
    Returns true if `f` is an executable file.
    '''
    if not f.exists():
        return False
    if not f.is_file():
        return False
    s = oct(f.stat().st_mode)[-3:]
    return '7' in s


def get_registered_commands(
    logger: logging.Logger, cmd_dict: dict[str, pathlib.Path] | None = None
) -> dict[str, AnyDict]:
    '''
    Returns a dictionary of namespaces with keys of str (representing the namespace)
    and values of dict, with keys of method names, and vals of dicts representing
    the arguments and docstrings.
    Error as appropriate.
    '''

    namespaces: dict[str, AnyDict] = {}
    if cmd_dict is None:
        return namespaces
    for namespace, path in cmd_dict.items():
        p = pathlib.Path(path)
        if not p.is_dir():
            raise ClippyConfigurationError(f'executable directory {p} does not exist')

        namespaces[namespace] = {}
        for f in p.iterdir():
            logger.debug(f"trying {f}")
            if _is_exe(f):
                fstr = os.fsdecode(f)
                logger.debug(f'running {fstr} {JSON_FLAG}')
                cmd: list[str] = [fstr, JSON_FLAG]
                try:
                    exe = subprocess.run(cmd, capture_output=True, check=True)
                    try:
                        j = json.loads(exe.stdout)
                        if not _check_version(j):
                            logger.warning('%s has an invalid or missing version - ignoring', fstr)
                        else:
                            ns = namespaces[namespace]
                            # print(f'adding {fstr} at version {j['version']} to namespace {ns}')
                            logger.debug('adding %s at version %s to namespace %s', fstr, j['version'], ns)
                            # test if this is a member function and defer to
                            # ooclippy if needed
                            if 'class_name' in j:
                                process_member_function(fstr, ns, j)
                            else:
                                j['exe_name'] = fstr
                                ns[j['method_name']] = j
                                logger.debug('Adding %s to valid commands under namespace %s', fstr, namespace)
                    except json.JSONDecodeError:
                        logger.warning('JSON parsing error for %s - ignoring', fstr)

                except subprocess.CalledProcessError as e:
                    logger.warning('%s exited with error code %s - ignoring', fstr, e.returncode)

    logger.debug(f"namespaces = {namespaces}")
    return namespaces
