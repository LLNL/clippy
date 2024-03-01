""" Clippy constants. """

DRY_RUN_FLAG = '--clippy-validate'
JSON_FLAG = '--clippy-help'
STATE_KEY = '_state'

# The name of the selector key in the meta.json files.
# these selectors cannot be dropped.
INITIAL_SELECTOR_KEY = 'initial_selectors'

# The name of the selector key in the json returns.
# If this key exists in the results
# then the selector hierarchy is replaced with its (processed) contents.
SELECTOR_KEY = '_selectors'
REAL = 'real'
STRING = 'string'
UINT = 'uint'
INT = 'int'
CLASS_META_FILE = 'meta.json'
