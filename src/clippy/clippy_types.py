# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT
"""
Defines types and classes for Clippy.
"""

import os
from typing import Any, Optional
from .error import ClippyConfigurationError

AnyDict = dict[str, Any]
CONFIG_ENTRY = tuple[Optional[str], Any]


class CLIPPY_CONFIG:
    def __init__(self, d):
        self._entries = d

    def get(self, field) -> Any:
        if field not in self._entries:
            raise ClippyConfigurationError(f"unknown configuration setting {field}")
        env, val = self._entries[field]
        if env is None:
            return val
        return os.environ.get(env, val)

    def _set(self, field: str, val: CONFIG_ENTRY):
        self._entries[field] = val


# PRIVATE: this dict contains the class types that clippy has constructed.
#          once constructed clippy will get the definition from this dict
#          to create new instances.
