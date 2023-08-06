"""
Logging facilities.
"""

import logging
from pkginfo import __title__

#: The logging object.
log = logging.getLogger(__title__)
log.setLevel(logging.WARNING)

# Add a stderr handler.
_handler = logging.StreamHandler()
_fmt = logging.Formatter("# %(message)s")
_handler.setFormatter(_fmt)
log.addHandler(_handler)


def set_verbose():
    log.setLevel(logging.INFO)
