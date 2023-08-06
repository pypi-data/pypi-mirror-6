import os
from setuptools import setup, find_packages
from apm import cmdname, __version__, __author__, __email__

setup(
    # required information
    name = cmdname,
    version = __version__,
    author = __author__,
    author_email = __email__,
    url = "https://github.com/dghubble/apm",

    # python packages
    packages = find_packages(),

    # provided packages
    provides = ["apm"],

    # required packages
    install_requires = [
    ],

    # scripts
    scripts = [
    ],

    # entry points
    entry_points = {
        "console_scripts": {
            "{} = apm.main:main".format(cmdname)
        }
    },

    # data
    package_data = {},

    # metadata
    description = "ansible package manager command line tool",
    long_description = open("README.rst").read(),
    license = "",
    keywords = "",
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        # extras
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools"],

)