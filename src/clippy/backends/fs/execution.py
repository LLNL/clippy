"""
    Functions to execute backend programs.
"""

from __future__ import annotations
import json
import logging
from subprocess import run, CompletedProcess
from ...clippy_types import AnyDict
from ... import cfg
from .constants import DRY_RUN_FLAG, HELP_FLAG

from ...error import ClippyValidationError, ClippyBackendError
from ..serialization import encode_clippy_json, decode_clippy_json


def _exec(
    cmd: list[str], submission_dict: AnyDict, logger: logging.Logger
) -> CompletedProcess:
    '''
    Internal function.

    Executes the command specified with `execcmd` and
    passes `submission_dict` as JSON via STDIN.

    Logs debug messages with progress.
    Returns the process result object.

    This function is used by _run and _validate. All options (pre_cmd and flags) should
    already be set.
    '''

    logger.debug(f'Submission = {submission_dict}')
    # PP support passing objects
    # ~ cmd_stdin = json.dumps(submission_dict)
    cmd_stdin = json.dumps(submission_dict, default=encode_clippy_json)

    logger.debug('Calling %s with input %s', cmd, cmd_stdin)
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
    '''
    Converts the dictionary dct into a json file and calls executable cmd with the DRY_RUN_FLAG.
    Returns True/False (validation successful) and any stderr.
    '''

    if isinstance(cmd, str):
        cmd = [cmd]

    execcmd = cfg.get('validate_cmd_prefix').split() + cmd + [DRY_RUN_FLAG]
    logger.debug('Validating %s', cmd)
    _, stderr = _exec_and_parse(execcmd, dct, logger, validate=True)
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
    output, _ = _exec_and_parse(execcmd, dct, logger, validate=False)

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
    output, _ = _exec_and_parse(execcmd, dct, logger, validate=True)

    return output or {}
