# -*- coding: utf-8 -*-
"""
    Core Repository and Role components for the manager.

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

import os
import shutil
import sys
import mmap
from apm.vcs.components import Repository
from apm.vcs.collections import VCSCommands, RepoHosts
from apm import cmdname
from apm import exceptions
from apm import utils


class RoleRepository(object):
    """
    A RoleRepository represents and manages a collection of role sources and 
    role packages kept inside a role repository home directory.

    Role sources and packages are kept isolated from one another in adjacent
    directory trees that mirror one another inside the role repository home
    directory.

    A single global RoleRepository should exist on a user's system, along with
    additional per-project RoleRepositories if desired.
    """
    # envvar to set custom global role repository location
    GLOBAL_PATH_ENVVAR = "APM_HOME"
    # default global role repository stored in ~/.apm
    DEFAULT_GLOBAL_PATH = os.path.join(utils.user_home(), ".apm")
    # full name of role used as template for initializing new roles 
    TEMPLATE_ROLE_NAME = "bitbucket.org/dghubble/base-role"

    @staticmethod
    def get_global_path():
        """Returns the global repository path, set via envvar or a default"""
        path = os.environ.get(RoleRepository.GLOBAL_PATH_ENVVAR)
        if path and os.path.isdir(path):
            return os.path.expanduser(path)
        else:
            return RoleRepository.DEFAULT_GLOBAL_PATH

    def __init__(self, repository_path=None):
        """
        Construct role repository and setup needed subdirectories of the
        repository_path.
        Raises RoleRepositoryException if repository_path cannot be created.
        """
        if not repository_path:
            repository_path = RoleRepository.get_global_path()
        self.repository_path = repository_path
        # repository's role sources directory
        self.sources_path = os.path.join(self.repository_path, "sources")
        # repository's role packages directory
        self.packages_path = os.path.join(self.repository_path, "roles")

        # ensure the repository_path and needed subdirectories exist.
        try:
            utils.upsert_directory(self.repository_path)
            utils.upsert_directory(self.sources_path)
            utils.upsert_directory(self.packages_path)
        except OSError as e:
            raise exceptions.RoleRepositorySetupException(e)

    def source_path(self, role_name):
        """Returns the path to the given role's source"""
        return os.path.join(self.sources_path, role_name)

    def package_path(self, role_name):
        """Returns the path to the given role's package"""
        return os.path.join(self.packages_path, role_name)

    def makeVCSRepository(self, role_name):
        """
        Given a full role_name string name, make a VCS repository 
        representation.
        """
        hosts = RepoHosts()
        if hosts.is_valid(role_name):
            host = hosts.host_for(role_name)
            # TODO - some hosts support multiple version control systems
            vcs_name = host.vcs_for(role_name)
            vcs_command = VCSCommands().by_name(vcs_name)
            repo_url = host.repo_url({"repo_root": role_name})
            repo = Repository(vcs_command, repo_url)
            return repo
        else:
            raise exceptions.HostUnsupported(role_name)

    def initialize(self, role_name):
        """
        Download the canonical role template source if needed. Update the
        template role. Create a new package role from it, named `role_name`.
        """
        template_role_name = RoleRepository.TEMPLATE_ROLE_NAME
        source_role = self._makeSourceRole(template_role_name)
        source_role.create()   # if already created, noop
        source_role.update()

        #TODO validate that role_name given is ok.
        package_role = self._makePackageRole(role_name, source_role.source_path)
        package_role.create()  #TODO, should clean create

    def get(self, role_name):
        """
        Download the source role `role_name`, along with all its dependencies.
        For each role downloaded, create a corresponding package role.
        """
        repo = self.makeVCSRepository(role_name)
        source_path = self.source_path(role_name)
        source_role = SourceRole(role_name, source_path, repo)
        # check if it exists first
        source_role.create()

        package_path = self.package_path(role_name)
        package_role = PackageRole(role_name, source_path, package_path)
        #TODO validate that role_name given is ok.
        package_role.create()

        # get_dependencies source and packages


    def update(self, role_name):
        """Update the role `role_name` to the latest version"""
        repo = self.makeVCSRepository(role_name)
        source_path = self.source_path(role_name)
        source_role = SourceRole(role_name, source_path, repo)
        source_role.update()

        # package_path = self.package_path(role_name)
        # package_role = PackageRole(role_name, source_path, package_path)
        # #TODO validate that role_name given is ok.
        # package_role.create()

    def _sources_list(self):
        """Returns list of role packages in the repository, by full role name"""
        roles = []
        for (dirpath, dirnames, filenames) in os.walk(self.sources_path):
            subpath = dirpath.replace(self.sources_path, "", 1)
            role_name = dirpath.replace(self.sources_path + os.sep, "", 1)
            role = Role(role_name, dirpath)
            if role.is_valid():
                roles.append(role)
            if subpath.count(os.sep) > 2:      # seems like a good limit
                dirnames[:] = []
        return roles

    def _packages_list(self):
        """Returns list of role packages in the repository."""
        roles = []
        for (dirpath, dirnames, filenames) in os.walk(self.packages_path):
            subpath = dirpath.replace(self.packages_path, "", 1)
            source_path = dirpath.replace("roles", "sources", 1)
            role_name = dirpath.replace(self.packages_path + os.sep, "", 1)
            role = PackageRole(role_name, dirpath, source_path)
            if role.is_valid():
                roles.append(role)
            if subpath.count(os.sep) > 2:      # seems like a good limit
                dirnames[:] = []
        return roles

    def list(self):
        for role in self._packages_list():
            role.check_warnings()
            print(role.source_path.replace(self.packages_path + os.sep, "", 1))

    def _prompt_remove(self, local_path):
        """
        Prompt and delete the directory at the local_path. Caller should
        be sure it is safe to delete this directory
        """ 
        choice = raw_input("Delete this directory and its contents? (y/n): ")
        if choice == "y":
            # delete directory and all contained files
            shutil.rmtree(local_path, ignore_errors=True)

    def clean(self, role_name):
        """
        Removes role `role_name`'s package contents from the repository, but
        preserves user varibles
        """ 
        role_source = self._makeSourceRole(role_name)
        role_package = self._makePackageRole(role_name)

        role_packages = self._packages_list()
        if remove_package and role_package in role_packages:
            print("Removing role {} located at {}.".format(
                role_package.name, role_package.package_path))
            role_package.clean()
        elif remove_package:
            raise exceptions.RoleNotFound(role_package.name, role_package.source_path)

    def remove(self, role_name):
        """
        Remove the role's source and package from the repository. Checks that
        the role_name is a valid role within the repository.
        """
        role_packages = self._packages_list()
        role_sources = self._sources_list()
        role_source = self._makeSourceRole(role_name)
        role_package = self._makePackageRole(role_name)
        
        if (role_package not in role_packages) and (role_source not in role_sources):
            raise exceptions.RoleNotFound(role_source.name, role_source.source_path)

        if role_package in role_packages:
            print("Removing role {} located at {}.".format(
                role_package.name, role_package.package_path))
            role_package.remove()
            
        if role_source in role_sources:
            print("Removing role {} located at {}.".format(
                role_source.name, role_source.source_path))
            role_source.remove()

    def _makeSourceRole(self, role_name):
        """Construct a SourceRole for `role_name`."""
        source_path = self.source_path(role_name)
        repo = self.makeVCSRepository(role_name)
        return SourceRole(role_name, source_path, repo)

    def _makePackageRole(self, role_name, source_path=None):
        """
        Construct a PackageRole for role `role_name`. Provide a source_path if 
        doing a one-off initialization from a template role source.
        """
        package_path = self.package_path(role_name)
        if not source_path:
            source_path = self.source_path(role_name)
        return PackageRole(role_name, source_path, package_path)


class Role(object):
    """
    A general Ansible Role with a fully qualified root name (e.g. 
    github.com/apmtool/base-role) and stored on a source_path.
    """
    ROLE_CLEAN_PROMPT = "Clean this role (delete all but user_vars)? (y/n): "
    ROLE_REMOVE_PROMPT = "Remove role directory and contents? (y/n): "

    def __init__(self, role_name, source_path):
        self.name = role_name           # full role name, i.e. role_name
        self.source_path = source_path  # path at which source will live

    def __eq__(self, other):
        """Role import names serve as unique identifiers."""
        return self.name == other.name

    def is_valid(self):
        """
        Validates whether the source_path directory contains an Ansible role. 

        Current implementation simply checks that meta/main.yml exists and 
        contains the text 'ansible'. Ansible galaxy roles should satisfy this 
        requirement via their galaxy_info.
        """
        main_meta = os.path.join(self.source_path, "meta/main.yml")
        if os.path.isfile(main_meta):
            with open(main_meta) as f:
                return "ansible" in f.read()
        else:
            return False

    def check_warnings(self):
        """
        Inspect the role at `source_path` and print any warnings about it's
        structure.
        """
        gitignore = os.path.join(self.source_path, ".gitignore")
        if os.path.isfile(gitignore):
            with open(gitignore) as f:
                if "user_vars/" not in f.read():
                    print("Warning: {} does not .gitignore user_vars/ !".format(
                            self.name))
        else:
            print("Warning: {} does not .gitignore user_vars/ !".format(
                            self.name))
            # cprint("Warning: {} does not .gitignore user_vars/ !".format(self.name))


class SourceRole(Role):
    """
    Role stored in a version control system to be cloned (or equiv.) to a local
    source path, updated periodically, used to create PackageRoles, and 
    possibly removed. 
    """

    def __init__(self, role_name, source_path, vcs_repo):
        super(SourceRole, self).__init__(role_name, source_path)
        self.repo = vcs_repo            # vcs repo of role source code

    def __str__(self):
        return "Role {} at {}".format(self.name, self.source_path)

    def create(self):
        """
        Clone the role source `repo` to the `source_path` on the local
        filesystem if there is no such directory. May raise 
        RoleDownloadException.
        If a `source_path` directory exists, no action is performed. 
        """
        repo_url = self.repo.url
        if os.path.isdir(self.source_path):
            print("Already fetched source for {}.".format(self.name))
        else:
            print("fetching source for {} ...".format(self.name))
            try:
                self.repo.vcs.create(repo_url, self.source_path)
            except Exception as e:
                raise exceptions.SourceRoleCreateException(self.name, e)

    def update(self):
        """
        Pulls the latest version of the source repository into the existing 
        repository located at the source_path.
        If update fails, raise CorruptedSourceException. If source_path does 
        not exist, raise MissingSourceException. 
        """
        repo_url = self.repo.url
        if os.path.exists(self.source_path):
            print("Updating {} source ...".format(self.name))
            try:
                self.repo.vcs.update(self.source_path)
            except Exception as e:
                raise exceptions.SourceRoleUpdateException(self.name, e)
        else:
            raise exceptions.MissingSourceException(self.name)

    @utils.make_prompt(Role.ROLE_CLEAN_PROMPT)
    def clean(self, exclude=["user_vars"]):
        """
        Remove contents *inside* the source path, but exclude the user_vars
        directory.
        """
        inside_package_dir = os.path.join(self.source_path, "")
        utils.rmtree(inside_package_dir, 
                     ignore_errors=True, 
                     onerror=None,
                     ignore=shutil.ignore_patterns(*exclude))

    @utils.make_prompt(Role.ROLE_REMOVE_PROMPT)
    def remove(self):
        """Remove the entire role source directory."""
        shutil.rmtree(self.source_path,
                      ignore_errors=True,
                      onerror=None)


class PackageRole(Role):
    """
    Role package which may be executed by Ansible itself, is built from a twin
    SourceRole at a specific version, and whose directory tree may contain
    user custom variables that should be respected.
    """

    def __init__(self, role_name, source_path, package_path):
        super(PackageRole, self).__init__(role_name, source_path)
        self.package_path = package_path # path at which package will live

    def __str__(self):
        return "Role {} at {}".format(self.name, self.source_path)

    def create(self):
        """
        Copy the tree at source_path to the package_path location, excluding
        the .git directory and its contents.
        """
        print("Creating {} package from source".format(self.name))
        utils.copytree(
            self.source_path,
            self.package_path,
            symlinks=False,   # follow symlinks instead of copying them
            ignore=shutil.ignore_patterns('*.git', "user_vars"))

    @utils.make_prompt(Role.ROLE_CLEAN_PROMPT)
    def clean(self, exclude=["user_vars"]):
        """
        Remove contents *inside* the package path, but exclude the user_vars
        directory.
        """
        inside_package_dir = os.path.join(self.package_path, "")
        utils.rmtree(inside_package_dir, 
                     ignore_errors=True, 
                     onerror=None,
                     ignore=shutil.ignore_patterns(*exclude))

    @utils.make_prompt(Role.ROLE_REMOVE_PROMPT)
    def remove(self):
        """Remove the entire role package directory."""
        shutil.rmtree(self.package_path,
                      ignore_errors=True,
                      onerror=None)





