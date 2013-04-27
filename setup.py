# If true, then the svn revision won't be used to calculate the
# revision (set to True for real releases)
RELEASE = False
#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages

# Get description and __version__ without using import
#readme = open("README.md", "rt").read()
#changes = open("CHANGES.md", "rt").read()
readme = open("readme_pypi.md", "rt").read()
g_dict = {}
exec(open("tabfix/_version.py").read(), g_dict)
version = g_dict["__version__"]

# 'setup.py upload' fails on Vista, because .pypirc is searched on 'HOME' path
import os
if not "HOME" in os.environ and  "HOMEPATH" in os.environ:
    os.environ.setdefault("HOME", os.environ.get("HOMEPATH", ""))
    print("Initializing HOME environment variable to '%s'" % os.environ["HOME"])


setup(name="tabfix",
      version = version,
      author = "Martin Wendt",
      author_email = "tabfix@wwwendt.de",
      maintainer = "Martin Wendt",
      maintainer_email = "tabfix@wwwendt.de",
      url = "https://github.com/mar10/tabfix",
      description = "Cleanup whitespace in text files",
#      long_description = main.__doc__,
      long_description = readme,# + "\n\n" + changes,

        #Development Status :: 2 - Pre-Alpha
        #Development Status :: 3 - Alpha
        #Development Status :: 4 - Beta
        #Development Status :: 5 - Production/Stable

      classifiers = ["Development Status :: 4 - Beta",
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
      keywords = "python indentation development tab spaces tool",
      license = "The MIT License",
#      package_dir = {"": "src"},
#      packages = find_packages(exclude=["ez_setup", ]),
      packages = ["tabfix"],

#      package_data={"": ["*.txt", "*.html", "*.conf"]},
      include_package_data = True,
      zip_safe = False,
      extras_require = {},
      test_suite = "tests.test_all",
      entry_points = {
          "console_scripts" : ["tabfix = tabfix.main:run"],
          },
      )
