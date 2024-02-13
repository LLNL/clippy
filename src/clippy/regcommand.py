# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

import pathlib
import json
import logging
import os
import subprocess
from clippy.error import ClippyConfigurationError
from clippy.ooclippy import processMemberFunction
from clippy.anydict import AnyDict

from typing import Dict, List, Optional, TYPE_CHECKING



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
    logger: logging.Logger,
    cmd_dict: Optional[Dict[str, pathlib.Path]] = None
) -> Dict[str, AnyDict]:
    '''
    Returns a dictionary of namespaces with keys of str (representing the namespace)
    and values of dict, with keys of method names, and vals of dicts representing
    the arguments and docstrings.
    Error as appropriate.
    '''

    namespaces: Dict[str, AnyDict] = {}
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
                cmd: List[str] = [fstr, JSON_FLAG]
                exe = subprocess.run(cmd, capture_output=True)
                if exe.returncode:
                    logger.warn(f'{fstr} exited with error code {exe.returncode} - ignoring')
                else:
                    try:
                        j = json.loads(exe.stdout)
                        ns = namespaces[namespace]
                        # test if this is a member function and defer to
                        # ooclippy if needed
                        if j.get('class_name', None) is not None:
                            processMemberFunction(fstr, ns, j)
                        else:
                            j['exe_name'] = fstr
                            ns[j['method_name']] = j
                            logger.debug(f'Adding {fstr} to valid commands under namespace {namespace}')
                    except json.JSONDecodeError:
                        logger.warn(f'JSON parsing error for {fstr} - ignoring')

    logger.debug(f"namespaces = {namespaces}")
    return namespaces
