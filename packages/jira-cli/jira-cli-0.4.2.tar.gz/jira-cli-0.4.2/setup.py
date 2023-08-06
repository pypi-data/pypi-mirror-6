"""
setup.py for jira-cli
"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org"
__copyright__ = "Copyright 2014, Ali-Akber Saifee"

import os
import sys
from setuptools import setup, find_packages, Command
import jiracli

this_dir = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS = filter(None, open(os.path.join(this_dir, 'requirements.txt')).read().splitlines())
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='jira-cli',
     author=__author__,
     author_email=__email__,
     url="http://github.com/alisaifee/jira-cli",
     license="MIT",
     version = jiracli.__version__,
     description = "command line utility for interacting with jira",
     long_description = open("README.rst").read(),
     classifiers = [k for k in open("CLASSIFIERS").read().split("\n") if k],
     packages = find_packages(exclude=['ez_setup']),
     include_package_data = True,
     zip_safe = False,
    install_requires = REQUIREMENTS,
     entry_points = {
         'console_scripts' : [
             'jira-cli = jiracli.cli:main',
             ]
        },
    **extra
     )

