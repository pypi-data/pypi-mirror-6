# -*- coding: utf-8 -*-
"""
    Subcommands implementing the features of the command line tool.

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

import os
import sys
import argparse
import tempfile
import zipfile
import tarfile
import shutil
from apm import cmdname
import subprocess

from apm import __version__

from apm.core import RoleRepository

from apm.exceptions import APMException

from apm.utils import with_envvars


ANSIBLE_ROLES_PATH_ENVVAR = "ANSIBLE_ROLES_PATH"
ANSIBLE_DEFAULT_HOST_LIST_ENVVAR = "DEFAULT_HOST_LIST"

def init(args):
    """
    Fetches and updates the Initializes a new role package from the latest 
    canonical role template.
    """

    # Determine whether in project or should be created in central place
    # Assume should be created in central
    role_name = args.role_name
    role_repository = RoleRepository()
    try:
        role_repository.initialize(role_name)
    except APMException as e:
        sys.exit(e)

@with_envvars(**{
    ANSIBLE_ROLES_PATH_ENVVAR: RoleRepository().packages_path,
    ANSIBLE_DEFAULT_HOST_LIST_ENVVAR: "localhost"})
def run(args):
    """
    Dispatch call to ansible-playbook with the given arguments unmodified.
    Sets Ansible environment variables within the execution to setup the roles
    path to point to the repository and to make the inventory default to 
    localhost.
    """
    pass_through_args = vars(args)["ansible_playbook_args"]
    ansible_playbook_args = ["ansible-playbook"] + pass_through_args
    subprocess.Popen(ansible_playbook_args).communicate()


def get(args):
    """
    Downloads a role package and its dependencies to the roles_home_path as
    a version controlled repository.
    """
    role_name = args.role_name
    role_repository = RoleRepository()
    try:
        role_repository.get(role_name)
    except APMException as e:
        sys.exit(e)

def update(args):
    """
    Updates a role package to latest master commit, by default.
    """
    role_name = args.role_name
    role_repository = RoleRepository()
    try:
        role_repository.update(role_name)
    except APMException as e:
        sys.exit(e)

def list(args):
    """Lists the role packages in the current role repository"""
    role_repository = RoleRepository()
    try:
        role_repository.list()
    except APMException as e:
        sys.exit(e)

def remove(args):
    """Removes a role package by deleting the role from the repository"""
    role_name = args.role_name
    role_repository = RoleRepository()
    try:
        role_repository.remove(role_name)
    except APMException as e:
        sys.exit(e)

def version(args):
    """Show version information"""
    print("{} {}".format(cmdname, __version__))
    sys.exit()





