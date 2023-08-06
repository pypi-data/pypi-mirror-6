# -*- coding: utf-8 -*-
"""
    Implements the base parser and help text formatting classes.

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

import argparse


class BaseArgParser(argparse.ArgumentParser):
    """Base parser which provides custom error handling behavior."""

    def error(self, message):
        """
        Upon parser error, prints parser help message instead of error trace
        """
        self.print_help()
        self.exit(2, "{}: error: {}\n".format(self.prog, message))
        #sys.exit(2)


class AlphabetizedHelpFormatter(argparse.HelpFormatter):
    """
    Formatting class for an ArgParser, which organizes optional arguments 
    alphabetically.
    """
    # http://stackoverflow.com/questions/12268602
    def add_arguments(self, actions):
        actions = sorted(actions, key=lambda a: a.option_strings)
        super(AlphabetizedHelpFormatter, self).add_arguments(actions)