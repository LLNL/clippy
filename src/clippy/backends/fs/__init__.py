""" Filesystem backend for clippy. """

from __future__ import annotations

import os
import json
import sys
import pathlib
import logging
from subprocess import CalledProcessError
from typing import Any


from .execution import _validate, _run, _help
from ..version import _check_version
from ..serialization import ClippySerializable

from ... import constants
from ...error import (
    ClippyConfigurationError,
    ClippyTypeError,
    ClippyValidationError,
    ClippyInvalidSelectorError,
)
from ...expressions import Selector
from ...utils import flat_dict_to_nested

from ...clippy_types import CLIPPY_CONFIG
from .config import _fs_config_entries

# create a fs-specific configuration.
cfg = CLIPPY_CONFIG(_fs_config_entries)

PATH = sys.path[0]


def get_cfg() -> CLIPPY_CONFIG:
    '''This is a mandatory function for all backends. It returns the backend-specific configuration.'''
    return cfg


def classes() -> dict[str, Any]:
    '''This is a mandatory function for all backends. It returns a dictionary of class name
    to the actual Class for all classes supported by the backend.'''
    from ... import cfg as topcfg  # pylint: disable=import-outside-toplevel

    paths = cfg.get('fs_backend_paths')
    _classes = {}
    # iterate over all (filesystem) paths and for those that aren't explicitly excluded,
    # create the class based on the directory name and add methods based on the executables
    # within the directory.
    for path in paths:
        files = os.scandir(path)
        for f in files:
            if f.name in cfg.get('fs_exclude_paths'):
                continue
            p = pathlib.Path(path, f)
            if os.path.isdir(p):
                _cls = _create_class(f.name, path, topcfg)
                _classes[f.name] = _cls
    return _classes


def _create_class(name: str, path: str, topcfg: CLIPPY_CONFIG):
    '''Given a name, a path, and a master configuration, create
    a class with the given name, and add methods based on the
    executable files within the class. Set convenience fields
    (_name, _path, _cfg) as well, and load class metadata from
    a meta.json file in each class directory. The meta.json
    file typically holds the class's docstring and any initial
    top-level selectors as a dictionary of selector: docstring.'''
    metafile = pathlib.Path(path, name, constants.CLASS_META_FILE)
    meta = {}
    if metafile.exists():
        with open(metafile, 'r', encoding='utf-8') as json_file:
            meta = json.load(json_file)
    # pull the selectors out since we don't want them in the class definition right now
    selectors = meta.pop(constants.INITIAL_SELECTOR_KEY, {})
    meta['_name'] = name
    meta['_path'] = path
    meta['_cfg'] = topcfg
    class_logger = logging.getLogger(topcfg.get('logname') + '.' + name)
    class_logger.setLevel(topcfg.get('loglevel'))
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
        class_logger.debug('adding %s to class', selector)
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

    # grab the help string, which gives us the docstring and  all arguments.
    cls.logger.debug('processing executable %s', executable)
    try:
        j = _help(executable, {}, cls.logger)

    except CalledProcessError as e:
        raise ClippyConfigurationError("Execution error " + e.stderr) from e

    # check to make sure we have the method name. This is so the executable can have
    # a different name than the actual method.
    if constants.METHODNAME_KEY not in j:
        raise ClippyConfigurationError("No method_name in " + executable)
    # check version
    if not _check_version(j):
        raise ClippyConfigurationError("Invalid version information in " + executable)

    docstring = j.get(constants.DOCSTRING_KEY, "")
    args = j.get(constants.ARGS_KEY, {})
    method = j[constants.METHODNAME_KEY]
    _define_method(cls, method, executable, docstring, args)
    return cls


def _define_method(
    cls, name: str, executable: str, docstr: str, arguments: list[str] | None
):  # pylint: disable=too-complex
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
        argdict[constants.STATE_KEY] = getattr(self, constants.STATE_KEY)
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
            if kw in outj.get(constants.REFERENCE_KEY, {}):
                kwval.clear()
                if isinstance(kwval, dict):
                    kwval.update(outj[kw])
                elif isinstance(kwval, list):
                    kwval += outj[kw]
                else:
                    raise ClippyTypeError()

        # dump any output
        if constants.OUTPUT_KEY in outj:
            print(outj[constants.OUTPUT_KEY])
        # update state according to json output
        if constants.STATE_KEY in outj:
            setattr(self, constants.STATE_KEY, outj[constants.STATE_KEY])

        # update selectors if necessary.
        if constants.SELECTOR_KEY in outj:
            d = flat_dict_to_nested(outj[constants.SELECTOR_KEY])
            for topsel, subsels in d.items():
                if not hasattr(self, topsel):
                    raise ClippyInvalidSelectorError(f'selector {topsel} not found in class; aborting')
                getattr(self, topsel)._import_from_dict(subsels)

        # return result
        if outj.get(constants.SELF_KEY, False):
            return self
        return outj.get(constants.RETURN_KEY)

        # end of nested def m

    # Add a new member function with name and implementation m to the class cls
    # setattr(name, '__doc__', docstr)
    m.__doc__ = docstr
    setattr(cls, name, m)
