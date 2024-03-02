"""
    Utility functions
"""

from .clippy_types import AnyDict
from .error import ClippyInvalidSelectorError
from .constants import SELECTOR_KEY


def flat_dict_to_nested(input_dict: AnyDict) -> AnyDict:
    """input dictionary has dot-delineated keys which are then parsed as subkeys.
    That is: {'a.b.c': 5} becomes {'a': {'_selectors': {'b': {'_selectors': {'c': {'__doc__' = 5}}}}}}
    """

    output_dict: AnyDict = {}
    for k, v in input_dict.items():
        # k is dotted
        if '.' not in k:
            raise ClippyInvalidSelectorError("cannot set top-level selectors")

        *path, last = k.split('.')
        curr_nest = output_dict
        for p in path:
            curr_nest.setdefault(p, {})
            curr_nest[p].setdefault(SELECTOR_KEY, {})
            curr_nest = curr_nest[p][SELECTOR_KEY]

        curr_nest.setdefault(last, {'__doc__': v})
    return output_dict
