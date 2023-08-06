"""
Configuration file.
"""

import os
from ConfigParser import RawConfigParser

from pkginfo import __title__
from logger import log


class DitzConfig(RawConfigParser):
    def __init__(self):
        RawConfigParser.__init__(self)

        self.add_defaults("install",
                          command="pyditz")

        self.add_defaults("html",
                          index_events=10,
                          release_events=10)

    def add_defaults(self, section, **defaults):
        """Add a section with defaults."""

        self.add_section(section)
        for key, val in defaults.items():
            self.set(section, key, val)

    def write_file(self, path):
        """Write config data to file."""

        with open(path, "w") as fp:
            fp.write("# %s configuration file.\n\n" % __title__)
            self.write(fp)


class Config(object):
    def __init__(self):
        homedir = os.path.expanduser("~")
        self.path = os.path.join(homedir, ".ditzrc")
        self.parser = None

    def set_file(self, path):
        self.path = path

    def __getattr__(self, attr):
        if not self.parser:
            self.parser = DitzConfig()
            log.info("reading %s" % self.path)
            self.parser.read(self.path)

        return getattr(self.parser, attr)


# Ditz user config settings.
config = Config()
