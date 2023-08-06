# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.recipe.script -- Buildout recipes to execute shell or python scripts
# :Creato:    dom 16 feb 2014 11:41:43 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from subprocess import check_call
import tempfile
import os, sys
import doctest


class Script(object):
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.install_script = options.get('install-' + sys.platform,
                                          options.get('install', ''))
        self.update_script = options.get('update-' + sys.platform,
                                         options.get('update', ''))

    def install(self):
        return self.execute(self.install_script) or tuple()

    def update(self):
        return self.execute(self.update_script) or tuple()


class ShellScript(Script):
    def make_script(self, script):
        script = script.strip()

        if not script:
            return

        lines = [l.strip() for l in script.split('\n')]
        if sys.platform == 'win32':
            scriptf = tempfile.NamedTemporaryFile(suffix=".bat", delete=False)
            lines.insert(0, '@echo off')
            # This is probably the wrong thing to do, but at least it seems
            # avoiding encoding errors
            lines.insert(1, 'chcp 65001')
        else:
            scriptf = tempfile.NamedTemporaryFile(delete=False)
            os.chmod(scriptf.name, 0o700)

        with scriptf as f:
            f.write('\n'.join(lines).encode('utf-8'))

        return scriptf.name

    def execute(self, script):
        script = self.make_script(script)
        if script:
            try:
                if sys.platform == 'win32':
                    check_call(script, shell=True)
                else:
                    check_call(['/bin/sh', script])
            finally:
                os.remove(script)


class PythonScript(Script):
    def __init__(self, buildout, name, options):
        super(PythonScript, self).__init__(buildout, name, options)

        b_options = buildout['buildout']
        links = options.get('find-links', b_options['find-links'])
        if links:
            links = links.split()
            options['find-links'] = '\n'.join(links)
        else:
            links = ()
        self.links = links

        index = options.get('index', b_options.get('index'))
        if index is not None:
            options['index'] = index
        self.index = index

        allow_hosts = b_options['allow-hosts']
        allow_hosts = tuple([host.strip()
                             for host in allow_hosts.split('\n') if host.strip()!=''])
        self.allow_hosts = allow_hosts

    def install_eggs(self):
        from zc.buildout.easy_install import install

        b_options = self.buildout['buildout']
        options = self.options

        eggs = options.get('eggs', None)
        if not eggs:
            return

        distributions = [r.strip() for r in eggs.strip().split('\n') if r.strip()]

        if distributions:
            ws = install(distributions, b_options['eggs-directory'],
                         links=self.links, index=self.index,
                         path=[b_options['develop-eggs-directory']],
                         newest=b_options.get('newest') == 'true',
                         allow_hosts=self.allow_hosts)
            for d in ws.require(distributions):
                d.activate()

    def execute(self, script):
        script = script.strip()

        if not script:
            return

        parser = doctest.DocTestParser()
        lines = [line.source for line in parser.parse(script)
                 if isinstance(line, doctest.Example)]
        script = '\n'.join(lines)
        self.install_eggs()
        locals = dict(buildout=self.buildout, options=self.options)
        exec(script, globals(), locals)
        if 'installed' in locals:
            installed = locals['installed']
            if installed and not isinstance(installed, (list, tuple)):
                installed = (installed,)
