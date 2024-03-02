""" Here be dragons. """

from __future__ import annotations

import logging
import importlib
from .config import _clippy_cfg
from .clippy_types import AnyDict, CLIPPY_CONFIG

cfg = CLIPPY_CONFIG(_clippy_cfg)

_dynamic_types: AnyDict = {}
# logging.basicConfig()
logfmt = logging.Formatter(cfg.get("logformat"))
logger = logging.getLogger(cfg.get("logname"))

handler = logging.StreamHandler()
handler.setFormatter(logfmt)
logger.addHandler(handler)
logger.setLevel(cfg.get("loglevel"))


def load_classes():
    for backend in cfg.get("backends"):
        b = importlib.import_module(f'.backends.{backend}', package=__name__)
        setattr(cfg, backend, b.get_cfg())
        for name, c in b.classes().items():
            # backend_config = importlib.import_module(f".backends.{name}.config.{name}_config")
            # for k, v in backend_config.items():
            #     cfg._set(k, v)

            globals()[name] = c


load_classes()
