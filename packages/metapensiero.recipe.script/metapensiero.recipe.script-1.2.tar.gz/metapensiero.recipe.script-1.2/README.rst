.. -*- coding: utf-8 -*-
.. :Progetto:  metapensiero.recipe.script
.. :Creato:    ven 07 mar 2014 18:13:50 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

Buildout helper recipes
=======================

This module implements two simple recipes to execute either a `shell` script (actually `batch`
scripts under M$-Windows) or a Python script.

Both recipes take two options, ``install`` and ``update``: both are considered as a list of
statements, one per line, that will be written in a temporary file that will be executed
respectively when the recipe is installed or updated. One or the other may be missing, and in
such case nothing will happen for that particular step.

When the commands to execute depend on the platform, they can be specified using the options
``install-linux`` or ``install-win32`` that have higher priority than the generic form.

Shell scripts
-------------

The ``metapensiero.recipe.script:shell`` recipe is implemented by the ``ShellScript`` class,
and can be used in the following way::

    [config]
    recipe = metapensiero.recipe.script:shell
    ini = config.ini
    install = ${buildout:bin-directory}/soladmin create-config ${:ini}

As said, some time the commands to execute depend on the particular platform they are run. In
such cases, you can say::

    [config]
    recipe = metapensiero.recipe.script:shell
    ini = config.ini
    install = ${buildout:bin-directory}/soladmin create-config ${:ini}
    install-win32 =
       ${buildout:bin-directory}/soladmin create-config ${:ini}
       echo Configuration created!
       pause

Python scripts
--------------

The ``metapensiero.recipe.script:python`` recipe is implemented by the ``PythonScript``
class. It is somewhat more powerful because it can easily access the whole buildout
configuration.

Consider the following example::

    [start_script]
    recipe = metapensiero.recipe.script:python
    install =
      >>> import sys
      >>> from os.path import join
      >>> basedir = buildout['buildout']['directory']
      >>> bindir = buildout['buildout']['bin-directory']
      >>> script = join(basedir, 'sol.bat' if sys.platform=='win32' else 'sol.sh')
      >>> config = join(basedir, buildout['config']['ini'])
      >>> with open(script, 'w') as f:
      >>>   if sys.platform == 'win32':
      >>>     f.write('@echo off\n')
      >>>   f.write('%s %s\n' % (join(bindir, 'solserver'), config))
      >>> installed = script

As you can see, the script can access other section settings thru the ``buildout`` local
variable, a dictionary that contains the whole buildout configuration. Another local variable
is ``options``, another dictionary containing the recipe settings.

The script may set the ``installed`` variable, that can be either a simple scalar string value
or a sequence of strings: it will be used as the result of the recipe, which usually is the
list of the files/directories installed by the recipe itself that will be deleted whenever the
recipe is removed from the configuration.

Using eggs
~~~~~~~~~~

If the Python script uses additional eggs, they can be specified with the ``eggs`` option, like
in the following example::

    [extjs]
    recipe = metapensiero.recipe.script:python
    eggs = metapensiero.extjs.desktop
    install =
      >>> from metapensiero.extjs.desktop.scripts.extjs_dl import download_and_extract, URL
      >>> download_and_extract(URL)
