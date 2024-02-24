# Copyright 2020 Lawrence Livermore National Security, LLC and other CLIPPy Project Developers.
# See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

""" The clippy configuration file. To be edited by users. """

from .anydict import AnyDict

# semver version restrictions for the backend
REQUIRED_BACKEND: str = '>=0.2.0, <0.3.0'

# flag for specifying a dry run to the backend
DRY_RUN_FLAG: str = '--clippy-validate'

# key to json entry that holds reference overrides from backend functions.
reference_key: str = 'references'

# key to json entry that holds return data from backend functions.
return_key: str = 'returns'

# command prefix used to specify clippy task management with the HPC cluster
# for instance, if using slurm this could be set to 'srun -n1 -ppdebug'
cmd_prefix: str = ''

# command prefix used to specify clippy task management with the HPC cluster
# for dry runs in certain environments. For instance, if using slurm this
# could be set to 'srun -n1 -ppdebug'
validate_cmd_prefix = ''

# contol the log level of clippy
loglevel: int = 0

# PRIVATE: this dict contains the class types that clippy has constructed.
#          once constructed clippy will get the definition from this dict
#          to create new instances.
_dynamic_types: AnyDict = {}
