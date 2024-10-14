"""
Application entry point.

Run the command-line application if arguments given, otherwise start the GUI.
"""

import logging
import sys

from . import command_line, gui


logger = logging.getLogger(__name__)


def main(options: command_line.Options) -> int:
    """
    Application entry point.

    Start GUI if no commmand-line options given.
    """
    match options.command:
        case 'discover':
            return command_line.run_discovery(options)
        case 'test':
            return command_line.run_device_test(options)
        case _:
            return gui.main(options)


if __name__ == '__main__':
    options = command_line.parse(sys.argv)
    logging.basicConfig(
        format="%(levelname)-7s %(message)s",
        level=logging.DEBUG if options.verbose else logging.INFO,
    )
    sys.exit(main(options))
