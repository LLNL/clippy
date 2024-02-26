""" Here be dragons. """

from __future__ import annotations

import logging
from . import config

# logging.basicConfig()
logfmt = logging.Formatter(config.CLIPPY_LOGFORMAT)
logger = logging.getLogger(config.CLIPPY_LOGNAME)

handler = logging.StreamHandler()
handler.setFormatter(logfmt)
logger.addHandler(handler)
logger.setLevel(config.CLIPPY_LOGLEVEL)


def load_classes():
    for backend in config.CLIPPY_BACKENDS:
        for name, c in backend.classes().items():
            globals()[name] = c


load_classes()
