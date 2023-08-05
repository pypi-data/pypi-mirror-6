# coding: utf-8

""" Spectroscopy Made Hard """

import os
import re
import sys

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

major, minor1, minor2, release, serial =  sys.version_info

readfile_kwargs = {"encoding": "utf-8"} if major >= 3 else {}

def readfile(filename):
    with open(filename, **readfile_kwargs) as fp:
        contents = fp.read()
    return contents

version_regex = re.compile("__version__ = \"(.*?)\"")
contents = readfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "smh",
    "__init__.py"))

#version = version_regex.findall(contents)[0]

setup(name="smh",
      version=0.1,
      author="Andrew R. Casey",
      author_email="andy@astrowizici.st",
      packages=["smh", "smh.gui"],
      url="http://www.github.com/andycasey/smh/",
      license="GPLv2",
      description="Spectroscopy Made Hard",
      long_description=readfile(os.path.join(os.path.dirname(__file__), "README.rst")),
      install_requires=readfile("requirements.txt").split()
     )
