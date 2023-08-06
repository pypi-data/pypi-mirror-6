# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Simple buildout recipes
# :Creato:    dom 16 feb 2014 11:37:31 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import os
from codecs import open

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

NAME = "metapensiero.recipe.script"

setup(name=NAME,
      version=VERSION,
      description="Buildout recipes to execute Python or Shell scripts",
      long_description=README + u'\n\n' + CHANGES,

      author='Lele Gaifax',
      author_email='lele@metapensiero.it',
      url="https://bitbucket.org/lele/metapensiero.recipe.script",

      license="GPLv3+",
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "License :: OSI Approved ::"
          " GNU General Public License v3 or later (GPLv3+)",
          "Framework :: Buildout",
          "Topic :: Software Development :: Build Tools",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],

      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['metapensiero', 'metapensiero.recipe'],

      install_requires=[
          'setuptools',
          'zc.buildout',
      ],

      tests_require=[
          'manuel',
          'zope.testing',
          'zc.buildout',
      ],
      test_suite='metapensiero.recipe.script.test.suite',

      entry_points={
          'zc.buildout': [
              'shell = %s:ShellScript' % NAME,
              'python = %s:PythonScript' % NAME,
          ]
      },
)
