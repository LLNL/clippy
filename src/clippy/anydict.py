# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT
"""
Defines the AnyDict type that will be used to identify
further typing optimizations.
"""

from typing import Any

AnyDict = dict[str, Any]
