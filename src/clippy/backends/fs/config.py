# pylint: disable=consider-using-namedtuple-or-dataclass
import os

_fs_config_entries = {
    # backend path for executables, in addition to the CLIPPY_BACKEND_PATH environment variable. Add to it here.
<<<<<<< HEAD
    "fs_backend_paths": (
        None,
        [x.strip() for x in os.environ.get("CLIPPY_BACKEND_PATH", "").split(":")],
    ),
    # exclude these directories from being made as classes.
    "fs_exclude_paths": ("CLIPPY_FS_EXCLUDE_PATHS", ["CMakeFiles"]),
=======
    'fs_backend_paths': (
        None,
        [x.strip() for x in os.environ.get('CLIPPY_BACKEND_PATH', '').split(':')],
    ),
    # exclude these directories from being made as classes.
    'fs_exclude_paths': ("CLIPPY_FS_EXCLUDE_PATHS", ['CMakeFiles']),
>>>>>>> 7cdf107e6908b75850182f2b637804bd69d2c336
}
