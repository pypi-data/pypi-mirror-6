# -*- coding: utf-8 -*-
"""
    The command line interface for the manager.

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

from apm import cmdname
from apm import subcommands
import argparse
from apm.parser import BaseArgParser, AlphabetizedHelpFormatter

class ToolCLI(object):
    """
    A command line interface for the manager tool. Encapsulates a parser 
    on which arguments and subcommand subparsers have been registered.
    """

    default_parser = BaseArgParser(
        description="ansible (role) package manager",
        epilog="For subcomamnd help, run `{} SUBCOMMAND -h`".format(cmdname),
        formatter_class=AlphabetizedHelpFormatter)

    def __init__(self, parser=default_parser):
        """
        Accepts an ArgParser subclass and registers arguments and subcommand
        subparsers on the parser to make it suitable for parsing the tool's
        command line arguments. If no parser is provided, a default one is used.
        """ 
        self._parser = parser
        subparsers = self._parser.add_subparsers(
            title="Available subcommands",
            description=None,
            # disable showing subcommands as {cmd1, cmd2, etc}
            metavar="")

        # create parser for 'init' subcommand.
        init_parser = subparsers.add_parser(
            "init", 
            help="initialize a new role package from the template")
        init_parser.add_argument(
            "role_name", 
            help="full name of role to be initialized (e.g. github.com/username/myrole)")
        init_parser.set_defaults(func=subcommands.init)

        # create parser for 'get' subcommand.
        get_parser = subparsers.add_parser(
            "get", 
            help="download a role package and its dependencies")
        get_parser.add_argument(
            "role_name", 
            help="role name (e.g. github.com/username/myrole)")
        get_parser.add_argument(
            "--no-deps",
            action="store_true",
            help="don't download role dependencies")
        get_parser.set_defaults(func=subcommands.get)

        # create parser for 'run' subcommand, which calls ansible-playbook.
        run_parser = subparsers.add_parser(
            "run",
            formatter_class=AlphabetizedHelpFormatter,
            help="run ansible playbook(s)")
        run_parser.add_argument("ansible_playbook_args", nargs=argparse.REMAINDER)
        run_parser.set_defaults(func=subcommands.run)

        # create parser for 'update' subcommand.
        update_parser = subparsers.add_parser(
            "update", 
            help="update a role package to latest commit")
        update_parser.add_argument(
            "role_name", 
            help="role name (e.g. github.com/username/myrole)")
        update_parser.set_defaults(func=subcommands.update)

        # create parser for 'remove' subcommand
        remove_parser = subparsers.add_parser(
            "remove", 
            help="remove a role package")
        remove_parser.add_argument(
            "role_name", 
            help="role name (e.g. github.com/username/myrole)")
        remove_parser.set_defaults(func=subcommands.remove)

        # create parser for 'list' subcommand
        list_parser = subparsers.add_parser(
            "list", 
            help="list the roles in the role repository")
        list_parser.set_defaults(func=subcommands.list)

        version_parser = subparsers.add_parser(
            "version",
            help="show version")
        version_parser.set_defaults(func=subcommands.version)

    @property
    def parser(self):
        return self._parser


