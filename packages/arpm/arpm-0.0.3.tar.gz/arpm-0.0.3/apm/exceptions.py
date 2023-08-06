#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Manager exceptions definitions.

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

from apm import cmdname
from apm import utils

class APMException(Exception):
    """Base Exception class"""
    def __str__(self):
        return self.msg

class RoleNotFound(APMException):
    def __init__(self, role_name, role_path):
        self.msg = "Role {} could not be found at {}".format(role_name, role_path)
        
class HostUnsupported(APMException):
    def __init__(self, role_root):
        self.msg = "role {} did not match any supported repository hosts".format(
            role_root)

class RoleRepositorySetupException(APMException):
    def __init__(self, exception):
        self.msg = "Failed to create role repository directory: {}".format(
            exception)

class SourceRoleCreateException(APMException):
    def __init__(self, role_name, exception):
        self.msg = "{} source repository could not be downloaded: {}".format(
            role_name, exception)

class MissingSourceException(APMException):
    def __init__(self, role_name):
        self.msg = ("No {} source found. You may need to get it first using: " 
                    "'{} get {}'").format(role_name, cmdname, role_name)

class SourceRoleUpdateException(APMException):
    def __init(self, role_name, exception):
        self.msg = "Problem updating {} source: {}".format(role_name, exception)