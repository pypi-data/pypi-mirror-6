# -*- coding: utf-8 -*-
"""
    descrc

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

from collections import StringToRepository
from apm.home import roles_path

def main():
    # vcs_git._run("../", "st")
    repo_string = "github.com/dghubble/homebrew-role"

    repo = StringToRepository().map(repo_string)
    repo.vcs_command.create("homebrew-role", repo.repo_url)
    # repo.vcs_command.ping("dtf", repo_string)

    # vcs_git.create(".", "github.com/dghubble/dghubble.com")

if __name__ == "__main__":
    main()







