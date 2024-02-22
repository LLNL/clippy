# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

from __future__ import annotations
import logging
import sys
import types
import uuid
import inspect
from collections.abc import Callable
from clippy.error import ClippyBackendError, ClippyTypeError
from clippy.regcommand import get_registered_commands
from clippy import config
from clippy.anydict import AnyDict
from clippy.execution import _validate, _run


#  Set this to the clippy executable flag that does validation of stdin.


class Command:
    '''
    An object that contains information relating to valid back-end commands.
    '''

    def __init__(self, namespace: str, name: str, session: "Clippy", jsondict: AnyDict):
        self.namespace = namespace
        self.name = name  # name of method
        self.session = session
        self.jsondict = jsondict
        self.positionals: AnyDict = {}
        for arg, argparams in self.args.items():  # self.args is defined below as a @property
            if argparams.get('position', -1) != -1:  # if position is not -1, this is a 0-indexed positional arg.
                self.session.logger.debug(f'  adding positional {arg} at {argparams["position"]}.')
                self.positionals[argparams['position']] = arg

    def genfn(self, docstring: str) -> Callable:
        '''
        Generates a function and sets its docstring.
        The returned function is used to dynamically
        create a method for a Clippy instance.
        '''

        # closure for self for the internal method, since it will be
        # shadowed within fn() otherwise.
        capself = self

        def fn(self, *args, **kwargs):
            # args are positional parameters, kwargs are named.
            # these are arguments to the command itself.
            self.logger.debug('Running Subcommand: ' + capself.name)
            self.logger.debug(f'  args = {args}, kwargs = {kwargs}')
            self.logger.debug(f'  positionals = {capself.positionals}')

            for i, arg in enumerate(args):
                if i not in capself.positionals:
                    self.logger.warn(f'Invalid positional argument "{arg}". Ignoring.')
                else:
                    posarg_name = capself.positionals[i]
                    if posarg_name in kwargs:  # we don't override dictionary with positionals.
                        self.logger.warning(
                            'Positional argument "%s" conflicts with dictionary argument %s "%s"; ignoring.',
                            arg,
                            posarg_name,
                            kwargs[posarg_name],
                        )

                    else:
                        kwargs[posarg_name] = arg

            (valid, warnings) = capself.session._validate_executable(capself.exe_name, kwargs)
            # if validate doesn't throw an error, we either have True (successful validation) or False
            # (warnings).
            if valid:  # no validation errors or warnings
                results = capself.session._call_executable(capself.exe_name, kwargs)
                references = results.get(config.reference_key, {})
                for kw, kwval in kwargs.items():
                    self.logger.debug('testing %s for overwrite against %s', kw, list(results.keys()))
                    if kw in references:
                        self.logger.debug('overwriting %s', kw)
                        kwval.clear()
                        if isinstance(kwval, dict):
                            kwval.update(references[kw])
                        elif isinstance(kwval, list):
                            kwval += references[kw]
                        else:
                            raise ClippyTypeError()
                return results.get(config.return_key, {})

            self.logger.warn(f'Validation returned warning: {warnings}; aborting execution')
            return {}

        f = fn
        f.__doc__ = docstring
        return f

    @property
    def args(self) -> AnyDict:
        return self.jsondict.get('args', {})

    @property
    def docstring(self) -> str:
        # we're probably overallocating here but whatever.
        posargs: list[tuple[str, AnyDict] | None] = [None] * len(self.args)
        optargs: list[tuple[str, AnyDict]] = []
        numpos = -1

        # sort the args into positional and optional.
        for arg, v in self.args.items():
            pos = v.get('position', -1)
            if pos == -1:
                optargs.append((arg, v))
            else:
                posargs[pos] = (arg, v)
                numpos = max(numpos, pos)

        numpos += 1
        posargs = posargs[:numpos]

        # make sure we have contiguous positional arguments.
        for p in posargs:
            if p is None:
                raise ClippyBackendError(f'Invalid options received for {self.namespace}/{self.name}')

        # example json:
        # {
        #   "args":{
        #       "i":{
        #           "desc":"first Number", "position":0, "required":true, "type":"number"
        #       },
        #      "j":{
        #           "desc":"second Number", "position":1, "required":true, "type":"number"
        #      }
        #   },
        #   "desc": "Sums to numbers",
        #   "method_name":"sum",
        #   "returns":{
        #       "desc":"i + j", "type":"number"
        #   }
        # }
        # build the docstring.
        docstring = f'{self.name}('
        posnames = [a[0] for a in posargs if a is not None]
        docstring += ", ".join(posnames)
        optnames = [f'{a[0]}={str(a[1].get("default_val", None))}' for a in optargs]
        docstring += ','.join(optnames)
        docstring += ')\n'
        docstring += '\n'
        docstring += f'{self.desc}\n'
        docstring += '\n'
        docstring += 'Parameters:\n'
        for a in posargs:
            if a is not None:
                docstring += f'{a[0]}: {a[1].get("type", "Unknown type")}\n'
                docstring += f'\t{a[1].get("desc", "No description.")}\n'

        for a in optargs:
            docstring += f'{a[0]}: {a[1].get("type", "Unknown type")}, default={str(a[1].get("default_val", None))}\n'
            docstring += f'\t{a[1].get("desc", "No description.")}\n'
        docstring += '\n'
        retname = self.returns.get('name', '')
        if retname:
            retname += ': '

        docstring += f'Returns: {retname} {self.returns.get("type", "Unknown type")}\n'
        docstring += f'\t{self.returns.get("desc", "No description")}\n'
        return docstring

    @property
    def method_name(self) -> str:
        return self.jsondict.get('method_name', self.name)

    @property
    def exe_name(self) -> str:
        return self.jsondict.get('exe_name', self.name)

    @property
    def desc(self) -> str:
        return self.jsondict.get('desc', 'No description')

    @property
    def returns(self) -> AnyDict:
        return self.jsondict.get('returns', {})


class Clippy:
    def __init__(self, clippy_cfg: AnyDict | None = None, cmd_prefix: str = '', loglevel: int | None = None):
        self.clippy_cfg = clippy_cfg
        self.cmd_prefix = cmd_prefix.split()
        self.namespaces: list[str] = []
        self.uuid = uuid.uuid4()
        self.logger = logging.getLogger(self.uuid.hex)
        handler = logging.StreamHandler(sys.stderr)
        self.logger.addHandler(handler)
        self.logger.setLevel(loglevel or config.loglevel)
        self.logger.info('Logger set to %s', self.logger.getEffectiveLevel())
        if clippy_cfg is not None:
            self.add_namespaces(clippy_cfg)

    def add_namespaces(self, cmd_dict: AnyDict):
        '''
        Adds namespaces to / replaces namespaces in a current
        Clippy object. Namespaces should be a dictionary
        {'name':'directory'}.

        If a namespace already exists with a given name,
        all methods within that namespace will be replaced
        by the methods from the new directory.
        '''
        j = get_registered_commands(self.logger, cmd_dict)
        for namespace, cmds in j.items():
            if namespace in self.namespaces:  # if the namespace exists, clear it out.
                self.logger.info('Replacing namespace %s', namespace)
                delattr(self, namespace)
            else:  # this is a new namespace. Let's add it to the list.
                self.logger.debug('Adding namespace %s', namespace)
                self.namespaces.append(namespace)

            inner = type(namespace, (), {})
            setattr(inner, 'methods', [])
            setattr(inner, 'classes', [])

            for name, jsondict in cmds.items():
                if not inspect.isclass(jsondict):
                    self.logger.debug('Adding registered command: %s', name)
                    cmd = Command(namespace, name, self, jsondict)
                    setattr(inner, name, types.MethodType(cmd.genfn(cmd.docstring), self))
                    inner.methods.append(name)  # type: ignore
                else:
                    self.logger.debug('%s is a class', name)
                    setattr(inner, name, jsondict)
                    inner.classes.append(name)  # type: ignore
            setattr(self, namespace, inner)

    def logo(self):
        logo()

    def _validate_executable(self, executable: str, submission_dict: AnyDict) -> tuple[bool, str | None]:
        '''
        Internal command.

        Runs the command in dry-run mode only, to validate input.
        Returns True or False if there are warnings (no errors),
        along with any stderr messageas.
        Calls _exec_and_parse.
        '''
        return _validate(executable, submission_dict, self.logger)

    def _call_executable(self, executable: str, submission_dict: AnyDict) -> AnyDict:
        '''
        Processes a submission locally (no remote server).
        Returns a Python dictionary of results.
        Calls _run.

        Assumes valid input.
        '''

        self.logger.debug('Running %s', executable)
        return _run(executable, submission_dict, self.logger)


def logo():
    print(
        '''
 ╭────────────────────────────────────╮
 │ It looks like you want to use HPC. │
 │ Would you like help with that?     │
 ╰────────────────────────────────────╯
  ╲
   ╲
    ╭──╮
    ⊙ ⊙│╭
    ││ ││
    │╰─╯│
    ╰───╯
'''
    )


logo()
