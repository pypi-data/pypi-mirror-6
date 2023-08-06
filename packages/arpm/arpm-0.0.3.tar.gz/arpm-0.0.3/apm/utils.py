#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Command line tool utility functions.

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

import os
import sys
import stat
import shutil

def user_home():
    """Gets the user home directory path across platforms."""
    return os.path.expanduser("~")

def upsert_directory(dir_path):
    """Create a directory at the given path, if it does not exist."""
    if os.path.isdir(dir_path):
        return
    else:
        os.makedirs(dir_path)

def copytree(src, dst, symlinks=False, ignore=None):
    """
    shutil.copytree recursive wrapper which will override existing files and 
    directories.
    Modified from Python 2.7.3 shutil.copytree source.
    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        if item in ignored_names:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            linkto = os.readlink(s)
            os.symlink(linkto, d)
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            # path doesn't exist, copy the file
            if not os.path.exists(d):
                shutil.copy2(s, d)
            # both exist, diff modification timees, then source always wins.
            # note that st_mtime granularity can be as coarse as 2 seconds on
            # FAT filesystems
            elif (os.stat(src).st_mtime != os.stat(dst).st_mtime):
                shutil.copy(s,d)

def rmtree(path, ignore_errors=False, onerror=None, ignore=None):
    """
    shutil.rmtree recursive wrapper which accepts a callable giving the
    directories to be ignored.

    Recursively delete a directory tree.

    If ignore_errors is set, errors are ignored; otherwise, if onerror
    is set, it is called to handle the error with arguments (func,
    path, exc_info) where func is os.listdir, os.remove, or os.rmdir;
    path is the argument to that function that caused it to fail; and
    exc_info is a tuple returned by sys.exc_info().  If ignore_errors
    is false and onerror is None, an exception is raised.

    """
    if ignore_errors:
        def onerror(*args):
            pass
    elif onerror is None:
        def onerror(*args):
            raise
    try:
        if os.path.islink(path):
            # symlinks to directories are forbidden, see bug #1669
            raise OSError("Cannot call rmtree on a symbolic link")
    except OSError:
        onerror(os.path.islink, path, sys.exc_info())
        # can't continue even if onerror hook returns
        return
    names = []
    try:
        names = os.listdir(path)
        if ignore is not None:
            ignored_names = ignore(path, names)
        else:
            ignored_names = set()
    except os.error, err:
        onerror(os.listdir, path, sys.exc_info())
    for name in names:
        if name in ignored_names:
            continue
        fullname = os.path.join(path, name)
        try:
            mode = os.lstat(fullname).st_mode
        except os.error:
            mode = 0
        if stat.S_ISDIR(mode):
            rmtree(fullname, ignore_errors, onerror, ignore)
        else:
            try:
                os.remove(fullname)
            except os.error, err:
                onerror(os.remove, fullname, sys.exc_info())
    try:
        os.rmdir(path)
    except os.error:
        onerror(os.rmdir, path, sys.exc_info())

def make_prompt(func, message="(y/n): "):
    """Returns a prompt decorator"""
    def prompt(func):
        """Prompt for y/no confirmation before executing the given `func`. Any
        response other than 'y' causes a NoOp.
        """
        def prompter(*args):
            choice = raw_input(message)
            if choice == "y":
                func(*args)
        return prompter

    return prompt


def with_envvars(**envvars):
    """
    Decorates the given function so that the environment variable definitions
    in `kwargs` are set within the context of execution and those environment
    variables are restored to their original values before returning to the 
    caller.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            old_vars = {}
            for var_name in envvars:
                # store old evvar value, or store None
                old_vars[var_name] = os.environ.get(var_name)
                # set envvar
                os.environ[var_name] = envvars[var_name]
            func(*args, **kwargs)
            # restore old evvars
            for var_name in old_vars:
                if old_vars[var_name]:
                    os.environ[var_name] = old_vars[var_name]
                else:
                    del os.environ[var_name]
        return wrapper

    return decorator






