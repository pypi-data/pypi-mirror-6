# -*- coding: utf-8 -*-
"""
    version control system collection

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

from components import VCSCommand
from components import Host
from components import Repository

git = VCSCommand(
    name="git",
    cmd="git",
    create_cmd="clone {repo_url} {target}",
    update_cmd="pull --ff-only",
    tag_cmd="????",
    tag_sync_cmd="checkout {tag_name}",
    tag_sync_default_cmd="checkout master",
    schemes=["git", "https", "http", "git+ssh"],
    ping_cmd="ls-remote {scheme}://{repo_root}"
    )

DEFAULT_VCS_LIST = [git]

class VCSCommands(object):
    """
    A collection of VCS (version control system) instances that should be
    made available for some purpose. 
    For example, many import systems allow several types of version controlled
    repositories to be fetched.
    """

    def __init__(self, version_system_commands=DEFAULT_VCS_LIST):
        """
        :param vcs_list: a list of version control systems to make available
        If not provided, just the `git` vcs will be available by default.
        """ 
        self.version_system_commands = version_system_commands

    def register(self, vcs_command):
        """
        Register an additional version control system commands
        """
        self.version_system_commands.append(vcs_command)

    def by_name(self, name):
        """Gets a VCS by name. Returns None if no VCS has the requested name."""
        for command in self.version_system_commands:
            if command.name == name.lower():
                return command
        return None

    def by_command(self, cmd):
        """
        Returns the first version control system with the given cmd. 
        Returns None if no version systems use the given cmd.
        """
        for command in self.version_system_commands:
            if command.cmd == cmd.lower():
                return command
        return None

github = Host(prefix="github.com/",
              regex="",
              vcs="git",
              repo_url_format="https://{repo_root}",
              check="")

bitbucket = Host(prefix="bitbucket.org/",
                 regex="",
                 vcs="git",
                 repo_url_format="https://{repo_root}",
                 check="")

DEFAULT_HOST_LIST = [github, bitbucket]


class RepoHosts(object):
    
    def __init__(self, hosts=DEFAULT_HOST_LIST):
        self.hosts = hosts

    def register(self, host):
        """Add a custom version controlled repository host"""
        self.hosts.append(host)

    def is_valid(self, repo_string):
        """
        Given a string repository name, returns whether the string matches
        any registered repo hosts.
        """
        return self.host_for(repo_string) is not None

    def host_for(self, repo_string):
        """
        Given a string repository name, returns first matching registered host
        found if any, otherwise None.
        """
        for host in self.hosts:
            if self.match(repo_string, host):
                return host
        return None

    def match(self, repo_string, host):
        """
        Returns true if the repo_string matches the host.

        The default implementation considers repo root uris that match the host
        prefix (TODO and regex) a True match. Override if a different mapping is
        desired.
        """
        return repo_string.startswith(host.prefix)



# class StringToRepositoryMapper(object):
#     """
#     May be extended to control how repo strings are mapped to repos.
#     """
#     hosts = HostList()

#     def __init__(self):
#         pass

#     def host_match(self, repo_string):
#         """
#         Returns the first host with a matching repo_root prefix. None if
#         no host prefix matches against the given repo_root.
#         """
#         for host in self.hosts:
#             if repo_string.startswith(host.prefix):
#                 return host
#         return None


    # def map(self, repo_string):
    #     """
    #     "Pass in a repository string representation, return a repository"
    #     assumes repo_string is the repo_root
    #     TODO, take variable number of args
    #     """
    #     host = self.host_match(repo_string)
    #     print host
    #     if host:
    #         # detect the VCS in use, hosts expose this differently
    #         vcs_name = host.vcs(repo_string)
    #         print vcs_name
    #         vcs = VCSList().byName(vcs_name)

    #         repo_url = host.repo_url({"repo_root": repo_string})
    #         repo = Repository(vcs, repo_url)
    #         return repo
    #     else:
    #         print("{} did not match a supported VCS host".format(repo_string))






