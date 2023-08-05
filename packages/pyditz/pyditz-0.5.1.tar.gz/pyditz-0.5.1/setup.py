# Setup script for Ditz.

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

import ditz
import ditz.version as info


setup(name             = info.__title__,
      author           = info.__author__,
      author_email     = info.__email__,
      description      = ditz.__doc__.strip(),
      long_description = open("README").read(),
      version          = info.__version__,
      license          = info.__license__,
      url              = info.__url__,
      classifiers      = info.__classifiers__.strip().split("\n"),

      packages = ["ditz"],
      include_package_data = True,

      setup_requires = [
          'setuptools_hg',
      ],

      install_requires = [
          'pyyaml >= 3.10',
          'jinja2 >= 2.7',
      ],

      tests_require = [
          'nose >= 1.3.0',
          'coverage >= 3.6',
          'mock >= 1.0.1',
      ],

      test_suite = 'nose.collector',

      entry_points = {
          'console_scripts': [
              'pyditz = ditz.console:main'
          ]
      })
