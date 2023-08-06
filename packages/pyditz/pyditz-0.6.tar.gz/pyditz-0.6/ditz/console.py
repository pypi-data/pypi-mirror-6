"""
Main console program.
"""

import sys
import argparse

from commands import DitzCmd
from config import config
from logger import set_verbose
from pkginfo import __version__


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(prog="pyditz")

    parser.add_argument("--version", action="version",
                        version="%(prog)s version " + __version__)

    group = parser.add_argument_group("global arguments")

    group.add_argument("-u", "--user-config", type=str, metavar="FILE",
                       help="use the given user config file")

    group.add_argument("-c", "--config-file", type=str, metavar="FILE",
                       help="use the given Ditz config file [NOT IMPLEMENTED]")

    group.add_argument("-i", "--issue-dir", type=str, metavar="DIR",
                       help="use the given issue directory [NOT IMPLEMENTED]")

    group.add_argument("-v", "--verbose", action="store_true",
                       help="be verbose about things")

    group = parser.add_argument_group("command arguments")

    group.add_argument("-m", "--comment", type=str, metavar="STRING",
                       help="specify a comment")

    group.add_argument("-n", "--no-comment", action="store_true",
                       help="skip asking for a comment")

    opts, args = parser.parse_known_args(args)
    cmdopts = dict(usecache=True, autosave=True, nocomment=opts.no_comment,
                   comment=opts.comment)

    if opts.user_config:
        config.set_file(opts.user_config)

    if opts.verbose:
        set_verbose()

    if not args:
        cmd = DitzCmd(interactive=True, **cmdopts)

        try:
            cmd.cmdloop()
        except KeyboardInterrupt:
            pass
    else:
        cmd = DitzCmd(**cmdopts)
        command = " ".join(args)
        if not cmd.onecmd(command):
            sys.exit(99)

if __name__ == "__main__":
    main()
