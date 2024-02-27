""" Here be dragons. """

from __future__ import annotations

import os
import json
import sys
import pathlib
import logging
from subprocess import CalledProcessError
from typing import Any


from . import config
from ..version import _check_version
from ..execution import _validate, _run
from ..expression import Selector
from ..serialization import ClippySerializable

from ... import config as topconfig
from ...constants import JSON_FLAG, CLASS_META_FILE, STATE_KEY, SELECTOR_KEY
from ...error import ClippyConfigurationError, ClippyTypeError, ClippyValidationError, ClippyInvalidSelectorError

PATH = sys.path[0]


def classes() -> dict[str, Any]:
    paths = config.CLIPPY_FS_BACKEND_PATHS
    _classes = {}
    for path in paths:
        files = os.scandir(path)
        for f in files:
            if f.name in config.CLIPPY_FS_EXCLUDE_PATHS:
                continue
            p = pathlib.Path(path, f)
            if os.path.isdir(p):
                _cls = _create_class(f.name, path)
                _classes[f.name] = _cls
    # cmds = get_registered_commands(logger, {'foo': pathlib.Path(origin, name)})
    # type(name, (), cmds)
    return _classes


# All backends must have a "classes" function that returns a class that can be added to Clippy.
def _create_class(name: str, path: str):
    metafile = pathlib.Path(path, name, CLASS_META_FILE)
    meta = {}
    if metafile.exists():
        with open(metafile, 'r', encoding='utf-8') as json_file:
            meta = json.load(json_file)
    # pull the selectors out since we don't want them in the class definition right now
    selectors = meta.pop(topconfig.initial_selector_key, {})
    meta['_name'] = name
    meta['_path'] = path
    class_logger = logging.getLogger(topconfig.CLIPPY_LOGNAME + '.' + name)
    class_logger.setLevel(topconfig.CLIPPY_LOGLEVEL)
    meta['logger'] = class_logger

    cls = type(name, (ClippySerializable,), meta)
    classpath = pathlib.Path(path, name)
    for file in os.scandir(classpath):
        fullpath = pathlib.Path(classpath, file)
        if os.access(fullpath, os.X_OK) and file.is_file():
            try:
                _process_executable(str(fullpath), cls)
            except ClippyConfigurationError as e:
                class_logger.warning("error processing %s: %s; ignoring", fullpath, e)

    # add the selectors
    # this should be in the meta.json file.
    for selector, docstr in selectors.items():
        print(f'adding {selector} to class')
        setattr(cls, selector, Selector(None, selector, docstr))
    return cls


def _process_executable(executable: str, cls):
    '''
    Stores the executable as a method of cls.
    details: The executable is queried for its description. The returned
             json file is parsed and converted to a type representing
             the executable's methods and state. The type is recorded in the
             symtable (by default globals()).
    '''

    cls.logger.debug('processing executable %s', executable)
    # name = os.path.basename(executable)
    cmd = [executable, JSON_FLAG]
    # open file, will be received through std out
    try:
        j = _run(cmd, {}, cls.logger)

    except CalledProcessError as e:
        raise ClippyConfigurationError("Execution error " + e.stderr) from e

    if 'method_name' not in j:
        raise ClippyConfigurationError("No method_name in " + executable)
    # check version
    if not _check_version(j):
        raise ClippyConfigurationError("Invalid version information in " + executable)

    docstring = j.get("desc", "")
    args = j.get("args", {})
    method = j["method_name"]
    _define_method(cls, method, executable, docstring, args)
    return cls


def _define_method(cls, name: str, executable: str, docstr: str, arguments: list[str] | None):
    '''Defines a method on a given class.'''

    def m(self, *args, **kwargs):
        '''
        Generic Method that calls an executable with specified arguments
        '''

        # special cases for __init__
        # call the superclass to initialize the _state
        if name == "__init__":
            super(cls, self).__init__()

        argdict = {}
        # statej  = {}

        # make json from args and state

        # .. add state
        # argdict[STATE_KEY] = self._state
        argdict[STATE_KEY] = getattr(self, STATE_KEY)
        # ~ for key in statedesc:
        #     ~ statej[key] = getattr(self, key)

        # .. add positional arguments
        numpositionals = len(args)
        for argdesc in arguments:
            value = arguments[argdesc]
            if "position" in value:
                if 0 <= value["position"] < numpositionals:
                    argdict[argdesc] = args[value["position"]]

        # .. add keyword arguments
        argdict.update(kwargs)

        # validate
        valid, stderr = _validate(executable, argdict, self.logger)
        if not valid:
            raise ClippyValidationError(stderr)

        # call executable and create json output
        outj = _run(executable, argdict, self.logger)

        # if we have results that have keys that are in our
        # kwargs, let's update the kwarg references. Works
        # for lists and dicts only.
        for kw, kwval in kwargs.items():
            if kw in outj.get(topconfig.reference_key, {}):
                kwval.clear()
                if isinstance(kwval, dict):
                    kwval.update(outj[kw])
                elif isinstance(kwval, list):
                    kwval += outj[kw]
                else:
                    raise ClippyTypeError()

        # update state according to json output
        if STATE_KEY in outj:
            setattr(self, STATE_KEY, outj[STATE_KEY])
            # self._state = outj[STATE_KEY]

            # ~ statedesc.clear();
            # ~ statej = outj["state"]
            # ~ for key in statej:
            #    ~ statedesc.append(key)
            #    ~ setattr(self, key, statej[key])

        if SELECTOR_KEY in outj:
            for topsel, subsels in outj['SELECTOR_KEY'].items():
                if not hasattr(self, topsel):
                    raise ClippyInvalidSelectorError(f'selector {topsel} not found in class; aborting')
                self.getaddr(topsel)._import_from_dict(subsels)

        # return result
        if outj.get('returns_self', False):
            return self
        return outj.get(topconfig.return_key)

        # end of nested def m

    # Add a new member function with name and implementation m to the class cls
    # setattr(name, '__doc__', docstr)
    m.__doc__ = docstr
    setattr(cls, name, m)
