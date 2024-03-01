"""
    Utility functions
"""

from .anydict import AnyDict
from .error import ClippyInvalidSelectorError


def flat_dict_to_nested(input_dict: AnyDict) -> AnyDict:
    """input dictionary has dot-delineated keys which are then parsed as subkeys.
    That is: {'a.b.c': 5} becomes {'a': {'subselectors': {'b': {'subselectors': {'c': 5}}}
    """

    output_dict: AnyDict = {}
    for k, v in input_dict.items():
        # k is dotted
        if '.' not in k:
            raise ClippyInvalidSelectorError("cannot set top-level selectors")

        *path, last = k.split('.')
        print(f'{path=}, {last=}, {output_dict=}')
        curr_nest = output_dict
        for p in path:
            print(f'  doing {p}')
            curr_nest.setdefault(p, {})
            curr_nest[p].setdefault('subselectors', {})
            print(f'  post-setdefault{curr_nest=}')
            curr_nest = curr_nest[p]['subselectors']

        curr_nest.setdefault(last, {'__doc__': v})
    return output_dict
