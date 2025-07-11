"""
    Functions to execute backend programs.
"""

from __future__ import annotations
import json
import logging
<<<<<<< HEAD

import subprocess
from ...clippy_types import AnyDict
from ... import cfg
from ...constants import OUTPUT_KEY
from .constants import (
    DRY_RUN_FLAG,
    HELP_FLAG,
    PROGRESS_INC_KEY,
    PROGRESS_SET_KEY,
    PROGRESS_START_KEY,
    PROGRESS_END_KEY,
)
=======
from subprocess import run, CompletedProcess
from ...clippy_types import AnyDict
from ... import cfg
from .constants import DRY_RUN_FLAG, HELP_FLAG
>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336

from ...error import ClippyValidationError, ClippyBackendError
from ..serialization import encode_clippy_json, decode_clippy_json

<<<<<<< HEAD
try:
    from tqdm import tqdm

    _has_tqdm = True
except ImportError:
    _has_tqdm = False


def _stream_exec(
    cmd: list[str],
    submission_dict: AnyDict,
    logger: logging.Logger,
    validate: bool,
) -> tuple[AnyDict | None, str | None]:
=======

def _exec(
    cmd: list[str], submission_dict: AnyDict, logger: logging.Logger
) -> CompletedProcess:
>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336
    '''
    Internal function.

    Executes the command specified with `execcmd` and
    passes `submission_dict` as JSON via STDIN.

    Logs debug messages with progress.
<<<<<<< HEAD
    Parses the object and returns a dictionary output.
=======
>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336
    Returns the process result object.

    This function is used by _run and _validate. All options (pre_cmd and flags) should
    already be set.
    '''

    logger.debug(f'Submission = {submission_dict}')
    # PP support passing objects
    # ~ cmd_stdin = json.dumps(submission_dict)
    cmd_stdin = json.dumps(submission_dict, default=encode_clippy_json)

    logger.debug('Calling %s with input %s', cmd, cmd_stdin)
<<<<<<< HEAD

    d = {}
    stderr = None
    with subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8'
    ) as proc:
        assert proc.stdin is not None
        assert proc.stdout is not None
        assert proc.stderr is not None

        proc.stdin.write(cmd_stdin + "\n")
        proc.stdin.flush()
        # proc.stdin.close()
        it = iter(proc.stdout.readline, '')
        progress = None
        for line in it:
            d = json.loads(line, object_hook=decode_clippy_json)
            if proc.poll() is not None:  # process terminated; this shouldn't normally happen.
                break
            if _has_tqdm:
                if progress is None:
                    if PROGRESS_START_KEY in d:
                        progress = tqdm() if d[PROGRESS_START_KEY] is None else tqdm(total=d[PROGRESS_START_KEY])
                        # print(f"start, total = {d[PROGRESS_START_KEY]}, {progress.n=}")
                else:
                    if PROGRESS_INC_KEY in d:
                        progress.update(d[PROGRESS_INC_KEY])
                        progress.refresh()
                        # print(f"update {progress.n=}")
                    if PROGRESS_SET_KEY in d:
                        progress.n = d[PROGRESS_SET_KEY]
                        progress.refresh()
                    if PROGRESS_END_KEY in d:
                        progress.close()
                        # print("close")
                        progress = None
            if progress is None:
                if OUTPUT_KEY in d:
                    print(d[OUTPUT_KEY])

        if proc.stderr is not None:
            stderr = "".join(proc.stderr.readlines())
    if progress is not None:
        progress.close()
    if proc.returncode:
        raise (ClippyValidationError(stderr) if validate else ClippyBackendError(stderr))

    if not d:
        return None, stderr
    if stderr:
        logger.debug('Received stderr: %s', stderr)
    logger.debug('run(): final stdout = %s', d)

    return (d, stderr)


def _validate(cmd: str | list[str], dct: AnyDict, logger: logging.Logger) -> tuple[bool, str]:
=======
    p = run(cmd, input=cmd_stdin, capture_output=True, encoding='utf-8', check=False)
    logger.debug('run(): result = %s', p)

    return p


def _parse(
    p: CompletedProcess, logger: logging.Logger, validate: bool
) -> tuple[AnyDict | None, str | None]:
    '''Given a CompletedProcess, process the output. Returns JSON dict
    from stdout and any stderr that has been generated.'''
    if p.returncode:
        raise (
            ClippyValidationError(p.stderr)
            if validate
            else ClippyBackendError(p.stderr)
        )

    if p.stderr:  # we have something on stderr, which is generally not good.
        logger.warning('Received stderr: %s', p.stderr)
    if not p.stdout:
        return None, p.stderr
    logger.debug('Received stdout: %s', p.stdout)
    return json.loads(p.stdout, object_hook=decode_clippy_json), p.stderr


def _exec_and_parse(
    cmd: list[str], submission_dict: AnyDict, logger: logging.Logger, validate: bool
) -> tuple[AnyDict | None, str | None]:
    '''Internal function. Calls _exec and _parse'''
    p = _exec(cmd, submission_dict, logger)
    return _parse(p, logger, validate)


def _validate(
    cmd: str | list[str], dct: AnyDict, logger: logging.Logger
) -> tuple[bool, str]:
>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336
    '''
    Converts the dictionary dct into a json file and calls executable cmd with the DRY_RUN_FLAG.
    Returns True/False (validation successful) and any stderr.
    '''

    if isinstance(cmd, str):
        cmd = [cmd]

    execcmd = cfg.get('validate_cmd_prefix').split() + cmd + [DRY_RUN_FLAG]
    logger.debug('Validating %s', cmd)
<<<<<<< HEAD

    _, stderr = _stream_exec(execcmd, dct, logger, validate=True)
=======
    _, stderr = _exec_and_parse(execcmd, dct, logger, validate=True)
>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336
    return stderr is not None, stderr or ''


def _run(cmd: str | list[str], dct: AnyDict, logger: logging.Logger) -> AnyDict:
    '''
    converts the dictionary dct into a json file and calls executable cmd. Prepends
    cmd_prefix configuration, if any.
    '''

    if isinstance(cmd, str):
        cmd = [cmd]
    execcmd = cfg.get('cmd_prefix').split() + cmd
    logger.debug('Running %s', execcmd)
    # should we do something with stderr?
<<<<<<< HEAD

    output, _ = _stream_exec(execcmd, dct, logger, validate=False)
=======
    output, _ = _exec_and_parse(execcmd, dct, logger, validate=False)

>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336
    return output or {}


def _help(cmd: str | list[str], dct: AnyDict, logger: logging.Logger) -> AnyDict:
    '''
    Retrieves the help output from the clippy command. Prepends validate_cmd_prefix
    if set and appends HELP_FLAG.
    Unlike `_validate()`, does not append DRY_RUN_FLAG, and returns the output.
    '''
    if isinstance(cmd, str):
        cmd = [cmd]
    execcmd = cfg.get('validate_cmd_prefix').split() + cmd + [HELP_FLAG]
    logger.debug('Running %s', execcmd)
    # should we do something with stderr?
<<<<<<< HEAD

    output, _ = _stream_exec(execcmd, dct, logger, validate=True)
=======
    output, _ = _exec_and_parse(execcmd, dct, logger, validate=True)

>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336
    return output or {}
