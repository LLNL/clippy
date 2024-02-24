"""
    Functions to execute backend programs.
"""

from __future__ import annotations
import json
import logging
from subprocess import run, CompletedProcess
from ..anydict import AnyDict
from .. import config

from ..error import ClippyValidationError, ClippyBackendError
from .serialization import encode_clippy_json, decode_clippy_json


def _exec(cmd: list[str], submission_dict: AnyDict, logger: logging.Logger, validate: bool) -> CompletedProcess:
    '''
    Internal function.

    Executes the command specified with `execcmd` and
    passes `submission_dict` as JSON via STDIN.

    Logs debug messages with progress.
    Returns the process result object.

    This function is used by _run and _validate.
    '''

    logger.debug(f'Submission = {submission_dict}')
    # PP support passing objects
    # ~ cmd_stdin = json.dumps(submission_dict)
    cmd_stdin = json.dumps(submission_dict, default=encode_clippy_json)

    if validate:
        execcmd = config.validate_cmd_prefix.split() + cmd + [config.DRY_RUN_FLAG]
    else:
        execcmd = config.cmd_prefix.split() + cmd

    logger.debug('Calling %s with input %s', execcmd, cmd_stdin)
    p = run(execcmd, input=cmd_stdin, capture_output=True, encoding='utf-8', check=False)
    logger.debug('run(): result = %s', p)

    return p


def _parse(p: CompletedProcess, logger: logging.Logger, validate: bool) -> tuple[AnyDict | None, str | None]:
    '''Given a CompletedProcess, process the output. Returns JSON dict
    from stdout and any stderr that has been generated.'''
    if p.returncode:
        raise ClippyValidationError(p.stderr) if validate else ClippyBackendError(p.stderr)

    if p.stderr:
        logger.warning('Received stderr: %s', p.stderr)
    if not p.stdout:
        return None, p.stderr
    logger.debug('Received stdout: %s', p.stdout)
    return json.loads(p.stdout, object_hook=decode_clippy_json), p.stderr


def _exec_and_parse(
    cmd: list[str], submission_dict: AnyDict, logger: logging.Logger, validate: bool
) -> tuple[AnyDict | None, str | None]:
    '''Internal function. Calls _exec and _parse'''
    p = _exec(cmd, submission_dict, logger, validate)
    return _parse(p, logger, validate)


def _validate(cmd: str | list[str], dct: AnyDict, logger: logging.Logger) -> tuple[bool, str]:
    '''
    Converts the dictionary dct into a json file and calls executable cmd.
    Returns true/false (validation successful) and any stderr.
    '''

    if isinstance(cmd, str):
        cmd = [cmd]
    logger.debug('Validating %s', cmd)
    _, stderr = _exec_and_parse(cmd, dct, logger, validate=True)
    return stderr is not None, stderr or ''


def _run(cmd: str | list[str], dct: AnyDict, logger: logging.Logger) -> AnyDict:
    '''
    converts the dictionary dct into a json file and calls executable cmd
    '''

    if isinstance(cmd, str):
        cmd = [cmd]
    logger.debug('Running %s', cmd)
    # should we do something with stderr?
    output, _ = _exec_and_parse(cmd, dct, logger, validate=False)

    return output or {}
