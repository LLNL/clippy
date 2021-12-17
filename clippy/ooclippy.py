# Copyright 2021 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT


import sys
import os
import inspect
import json

# ~ from pprint import pprint
from subprocess import run
from subprocess import PIPE
from clippy.error import ClippyBackendError, ClippyConfigurationError
from clippy.error import ClippyValidationError, ClippyClassInconsistencyError

##
## clippy flags

DRY_RUN_FLAG = '--clippy-validate'
JSON_FLAG = '--clippy-help'
STATE_KEY = '__state__'


##
## new functions

def createMetaclass(name, docstring):
    '''
    Creates a new class name, docstring, and underlying executable.
    '''
    clsdct = {"__doc__": docstring}
    cls = type(name, (object,), clsdct)

    # set an empty object state
    cls.__state__ = {}
    return cls


def checkMetaclassConsistency(cls, name, docstring):
    if getattr(cls, "__name__", None) != name:
        raise ClippyClassInconsistencyError()

    if getattr(cls, "__doc__", None) != docstring:
        raise ClippyClassInconsistencyError()




def callExecutable(executable, dct):
    '''
    converts the dictionsary dct into a json file and calls executable cmd
    '''

    cmd_stdin = json.dumps(dct)

    # was: p = subprocess.run(execcmd, input=cmd_stdin, capture_output=True, encoding='ascii')
    # works also with older pythons
    p = run([executable], input=cmd_stdin, stdout=PIPE, encoding='ascii')

    if p.returncode:
        raise ClippyBackendError(p.stderr)

    # self.logger.debug(f'Received stdout: {p.stdout}')
    # if p.stderr:
    #    self.logger.warn(f'Received stderr: {p.stderr}')

    # if we have no output, we still need SOMETHING to feed json.loads, so let's set it to a scalar 'null'.
    output = 'null' if not p.stdout else p.stdout
    return output


def validateExecutable(executable, dct):
    '''
    converts the dictionsary dct into a json file and calls executable cmd
    '''

    cmd_stdin = json.dumps(dct)

    # was: p = subprocess.run(execcmd, input=cmd_stdin, capture_output=True, encoding='ascii')
    # works with older pythons
    p = run([executable, DRY_RUN_FLAG], input=cmd_stdin, stdout=PIPE, encoding='ascii')

    if p.returncode:
        raise ClippyValidationError(p.stderr)

    warn = ''
    ret = True
    if p.stderr:
        # self.logger.warn(f'Received {p.stderr}')
        ret = False
        warn = p.stderr

    # self.logger.debug(f'Validation returning {ret}')
    return (ret, warn)



def defineMethod(cls, name, executable, arguments):
    def m(self, *args, **kwargs):
        '''
        Generic Method that calls an executable with specified arguments
        '''

        argdict = {}
        statej  = {}

        # make json from args and state

        # .. add state
        argdict[STATE_KEY] = cls.__state__
        # ~ for key in statedesc:
            # ~ statej[key] = getattr(self, key)

        # .. add positional arguments
        numpositionals = len(args)
        for argdesc in arguments:
            value = arguments[argdesc]
            if "position" in value:
                if value["position"] >= 0 and value["position"] < numpositionals:
                    argdict[argdesc] = args[value["position"]]

        # .. add keyword arguments
        for key, value in kwargs.items():
            argdict[key] = value

        # validate
        validateExecutable(executable, argdict)

        # call executable and create json output
        output = callExecutable(executable, argdict)

        outj = json.loads(output)

        # update state according to json output
        if STATE_KEY in outj:
            cls.__state__ = outj[STATE_KEY]

            # ~ statedesc.clear();
            # ~ statej = outj["state"]
            # ~ for key in statej:
                # ~ statedesc.append(key)
                # ~ setattr(self, key, statej[key])

        # return result
        if "returns" in outj:
            return outj["returns"]

        # todo: test if "result" is part of the description
        return None
        # end of nested def m

    # Add a new member function with name and implementation m to the class cls
    setattr(cls, name, m)


# obsolete
# ~ def defineAPI(cls, apidesc, statedesc):
    # ~ '''
    # ~ Adds methods to cls according to the description in apidesc
    # ~ '''

    # ~ for el in apidesc:
        # ~ defineMethod(cls, el["method"], el["args"], statedesc)
        # ~ print('+ ' + el["method_name"])


def processExecutable(executable, symtable):
    '''
    Creates a class representing the executable, and stores the created class in symtable.
    details: The executable is queried for its description. The returned
             json file is parsed and converted to a type representing
             the executable's methods and state. The type is recorded in the
             symtable (by default globals()).
    '''

    cmd = [executable, JSON_FLAG]
    # open file, will be received through std out
    exe = run(cmd, stdout=PIPE)

    if exe.returncode:
        raise ClippyConfigurationError("Execution error " + str(exe.returncode))

    j = json.loads(exe.stdout)

    metaclassname = j["class_name"]
    docstring     = j["class_desc"]
    method        = j["method_name"]
    args          = j["args"] if "args" in j else {}

    # check if metaclass exists already
    if metaclassname in symtable:
        # reuse existing class
        metaclass = symtable[metaclassname]
        checkMetaclassConsistency(metaclass, metaclassname, docstring)
    else:
        # create a new metaclass
        metaclass = createMetaclass(metaclassname, docstring)
        symtable[metaclassname] = metaclass

    # add the methods
    defineMethod(metaclass, method, executable, args)
    return metaclass


def processDirectory(directory, recurse_directories = False, symtable = None):
    '''
    Processes all executables in a directory.
    '''

    if symtable is None:
        symtable = inspect.currentframe().f_back.f_locals

    for el in os.scandir(directory):
        if os.access(el, os.X_OK):
            if el.is_file():
                processExecutable(el, symtable)
            elif recurse_directories and el.is_dir():
                processDirectory(el, True, symtable)


##
## main (simple tester)

# ~ if __name__ == "__main__":
    # ~ processDirectory("./bin/howdy")

    # ~ # create default greeter
    # ~ g = Greeter()
    # ~ print(g.greet())

    # ~ # create a new greeter
    # ~ g = Greeter("Howdy", name = "Texas")
    # ~ print(g.greet())

    # ~ # reset state
    # ~ g.setGreeting("Hello")
    # ~ g.setGreeted("Dude")
    # ~ print(g.greet())

    # ~ pprint(g)
    # ~ pprint(Greeter)
    # ~ sys.exit(0)

