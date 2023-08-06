# -*- coding: utf-8 -*-
"""
    descrc

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

import subprocess

class VCSCommand(object):
    """
    Describes how to use a version control system such as Git, Mercurial, or
    Subversion.
    """
    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.cmd = kwargs["cmd"]
        self.create_cmd = kwargs["create_cmd"]
        self.update_cmd = kwargs["update_cmd"]
        self.tag_cmd = kwargs["tag_cmd"]
        self.schemes = kwargs["schemes"]
        self.ping_cmd = kwargs["ping_cmd"]

    def _run(self, cmdline, keyvals, cwd):
        """
        Runs the command line cmd in the given directory.
        Returns the a tuple 
        """
        # check that git is installed

        # 0th argument is always the name of the command
        cmdline = cmdline.format(**keyvals)
        args = [self.cmd] + cmdline.split()
        (stdout_data, stderr_data) = subprocess.Popen(args, cwd=cwd).communicate()
        return (stdout_data, stderr_data)

    def create(self, repo_url, target, cwd="."):
        self._run(self.create_cmd, {"repo_url": repo_url, "target": target}, cwd)

    def update(self, cwd="."):
        self._run(self.update_cmd, {}, cwd)

    def ping(self, scheme, repo, cwd="."):
        self._run(self.ping_cmd, {"scheme": scheme, "repo": repo}, cwd)


class Host(object):
    """
    Host of version controlled repositories
    """

    def __init__(self, prefix, regex, vcs, repo_url_format, check):
        self.prefix = prefix
        self.regex = regex
        self._vcs = vcs
        self.repo_url_format = repo_url_format
        self.check = check

    def vcs_for(self, repo_string):
        """More complex behavior needed for some hosts"""
        return self._vcs

    def repo_url(self, kwargs):
        return self.repo_url_format.format(**kwargs)


class Repository(object):
    """Structured representation of a version controlled repository"""

    def __init__(self, vcs_command, repo_url):
        """
        :param vcs_command: a VCSCommand instance
        :param repo_url: repository url, including the scheme
        """
        self.vcs = vcs_command
        self.url = repo_url








