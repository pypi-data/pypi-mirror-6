#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Entry point for the command line tool.

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

import sys
from apm.cli import ToolCLI


def main():
    """
    Constructs a ToolCLI for the tool, parses command line args, and calls 
    the chosen subcommand.
    """
    cli_parser = ToolCLI().parser

    # only the implicitly passed command name was passed, no arguments
    if len(sys.argv) == 1:
        sys.exit(cli_parser.print_help())

    args = cli_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()