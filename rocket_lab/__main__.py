"""
Application entry point.

Run the command-line application if arguments given, otherwise start the GUI.
"""

import logging
import sys

from . import command_line


logger = logging.getLogger(__name__)


def main(options: command_line.Options) -> int:
    """
    Application entry point.

    Start GUI if no commmand-line options given.
    """
    match options.command:
        case 'discover':
            return command_line.discover(options)
        case _:
            return start_gui()


def start_gui() -> int:
    logger.info("Starting GUI...")
    return 0


if __name__ == '__main__':
    options = command_line.parse(sys.argv)
    logging.basicConfig(
        format="%(levelname)-7s %(message)s",
        level=logging.DEBUG if options.verbose else logging.INFO,
    )
    sys.exit(main(options))
