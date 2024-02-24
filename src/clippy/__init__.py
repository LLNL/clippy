""" Here be dragons. """

from __future__ import annotations

import logging
from . import config

logger = logging.Logger('clippy')
logger.setLevel(logging.DEBUG)


def load_classes():
    for backend in config.CLIPPY_BACKENDS:
        for name, c in backend.classes().items():
            globals()[name] = c


load_classes()
