.. -*- coding: utf-8 -*-
.. :Progetto:  metapensiero.recipe.script -- Doctests
.. :Creato:    sab 08 mar 2014 13:33:42 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

Automated tests
===============

We need a config file::

  >>> cfg = """
  ... [buildout]
  ... parts = test
  ...
  ... [test]
  ... recipe = metapensiero.recipe.script:shell
  ... install=%s
  ... """

  >>> test_file = join(sample_buildout, 'test.txt')
  >>> cmds = 'echo "yeah" > %s' % test_file
  >>> write(sample_buildout, 'buildout.cfg', cfg % cmds)

Ok, so now we can touch a file for testing::

  >>> print(system(buildout))
  Installing test...

  >>> 'test.txt' in os.listdir(sample_buildout)
  True

And remove it::

  >>> test_file = join(sample_buildout, 'test.txt')
  >>> if sys.platform == 'win32':
  ...    cmds = 'del %s' % test_file
  ... else:
  ...    cmds = 'rm %s' % test_file
  >>> write(sample_buildout, 'buildout.cfg', cfg % cmds)

  >>> print(system(buildout))
  Uninstalling test.
  Installing test...

  >>> 'test.txt' in os.listdir(sample_buildout)
  False

The same could be written as::

  >>> test_file = join(sample_buildout, 'test.txt')
  >>> cmds = 'echo "yeah" > %s' % test_file
  >>> write(sample_buildout, 'buildout.cfg', cfg % cmds)
  >>> print(system(buildout))
  Uninstalling test.
  Installing test...

  >>> 'test.txt' in os.listdir(sample_buildout)
  True

  >>> deletecfg = """
  ... [buildout]
  ... parts = test
  ...
  ... [test]
  ... recipe = metapensiero.recipe.script:shell
  ... install=rm %(testfile)s
  ... install-win32=del %(testfile)s
  ... """

  >>> test_file = join(sample_buildout, 'test.txt')
  >>> write(sample_buildout, 'buildout.cfg', deletecfg % dict(testfile=test_file))
  >>> print(system(buildout))
  Uninstalling test.
  Installing test...

  >>> 'test.txt' in os.listdir(sample_buildout)
  False

Or even as a Python script::

  >>> pycfg = """
  ... [buildout]
  ... parts = test
  ...
  ... [test]
  ... recipe = metapensiero.recipe.script:python
  ... install=
  ...  >>> from os.path import join
  ...  >>> boptions = buildout['buildout']
  ...  >>> testfile = join(boptions['directory'], 'test.txt')
  ...  >>> with open(testfile, 'w') as f:
  ...  >>>   f.write('yeah')
  ...  >>> installed = testfile
  ... """

  >>> write(sample_buildout, 'buildout.cfg', pycfg)
  >>> print(system(buildout))
  Uninstalling test.
  Installing test...

  >>> 'test.txt' in os.listdir(sample_buildout)
  True

This time the test file gets automatically deleted::

  >>> pyemptycfg = """
  ... [buildout]
  ... parts =
  ... """

  >>> write(sample_buildout, 'buildout.cfg', pyemptycfg)
  >>> print(system(buildout))
  Uninstalling test...

  >>> 'test.txt' in os.listdir(sample_buildout)
  False
