#!/usr/bin/env python
import os
from setuptools import setup

# If true, then the svn revision won't be used to calculate the
# revision (set to True for real releases)
RELEASE = False

# Get description and __version__ without using import
readme = open("readme_pypi.rst", "rt").read()
g_dict = {}
exec(open("tabfix/_version.py").read(), g_dict)
version = g_dict["__version__"]

# 'setup.py upload' fails on Vista, because .pypirc is searched on 'HOME' path
if "HOME" not in os.environ and "HOMEPATH" in os.environ:
    os.environ.setdefault("HOME", os.environ.get("HOMEPATH", ""))
    print("Initializing HOME environment variable to '%s'" % os.environ["HOME"])

setup(
    name="tabfix",
    version=version,
    author="Martin Wendt",
    author_email="tabfix@wwwendt.de",
    maintainer="Martin Wendt",
    maintainer_email="tabfix@wwwendt.de",
    url="https://github.com/mar10/tabfix",
    description="Cleanup whitespace in text files",
    long_description=readme,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
         "Programming Language :: Python :: 2",
         "Programming Language :: Python :: 3",
         "Topic :: Software Development :: Libraries :: Python Modules",
         "Topic :: Utilities",
         ],
    keywords="python indentation development tab spaces tool",
    license="The MIT License",
    packages=["tabfix"],
    include_package_data=True,
    zip_safe=False,
    extras_require={},
    test_suite="tests.test_all",
    entry_points={
        "console_scripts": ["tabfix = tabfix.main:run"],
        },
    )
