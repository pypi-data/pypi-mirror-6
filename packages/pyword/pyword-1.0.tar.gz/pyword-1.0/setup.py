# Setup script for pyword.

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup

import myword

# Add Windows install script if required.
if sys.platform == 'win32':
    scripts = ["win32/myword-install"]
else:
    scripts = []

# Set things up.
setup(name             = "pyword",
      author           = myword.__author__,
      author_email     = myword.__email__,
      description      = myword.__doc__.strip(),
      long_description = open("README").read(),
      version          = myword.__version__,
      license          = myword.__license__,
      url              = myword.__url__,
      classifiers      = myword.__classifiers__.strip().split("\n"),

      packages = ["myword"],
      scripts = scripts,
      include_package_data = True,

      setup_requires = [
          'setuptools_hg',
      ],

      entry_points = {
          'gui_scripts': [
              'myword = myword.game:play'
          ]
      })
