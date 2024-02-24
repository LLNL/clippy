import os

# backend path for executables, in addition to the CLIPPY_BACKEND_PATH environment variable. Add to it here.
CLIPPY_FS_BACKEND_PATHS = [
    x.strip() for x in os.environ.get('CLIPPY_BACKEND_PATH', '').split(':')
]

# exclude these directories from being made as classes.
CLIPPY_FS_EXCLUDE_PATHS = ['CMakeFiles']
