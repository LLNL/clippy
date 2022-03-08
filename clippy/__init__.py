# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

import warnings
from clippy.clippy import Clippy
import inspect

class ClippyRebindWarning(UserWarning):
    pass

def clippy_import(backend_path, namespace=None):
    """
    Imports clippy-wrapped functions into the local python environment. 

    backend_path is a string file path to a directory containing backend function executables

    example usages include:

    ```
    # import functions in examples
    clippy_import("/path/to/examples")

    howdy("seth") # imported from the examples directory and bound locally
    ```

    ```
    # import functions in examples into a namespace bound locally
    clippy_import("/path/to/examples", namespace="examples")

    examples.howdy("Seth")
    ```

    backend_path: string
    namespace: string
    """
    if namespace:
        backend_config = {namespace: backend_path}
    else:
        backend_config = {str(hash(backend_path)): backend_path}

    c = Clippy(backend_config)

    caller_locals = inspect.currentframe().f_back.f_locals
    
    if namespace:
        # TODO on subsequent calls to clippy_import we want to 
        #      union the members of the namespace with any existing 
        #      namespace. Currently this only allows a namespace 
        #      (and thus it's members) to be added once.
        _bind_to_local_environment(caller_locals, c, namespace)
    else:    
        for ns in backend_config:
            nsobj = getattr(c, ns)
            for fn_name in nsobj.methods:
                _bind_to_local_environment(caller_locals, nsobj, fn_name)
            for class_name in nsobj.classes:
                _bind_to_local_environment(caller_locals, nsobj, class_name)
    
def _bind_to_local_environment(caller_locals, src_obj, src_name):
    if src_name in caller_locals:
        warnings.warn(f"{src_name} already exists in local environment, skipping rebind...", ClippyRebindWarning)
        return
    caller_locals[src_name] = getattr(src_obj, src_name)
