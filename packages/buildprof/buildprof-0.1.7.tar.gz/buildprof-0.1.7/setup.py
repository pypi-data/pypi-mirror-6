#!/usr/bin/env python
#
# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import json
import os
import setuptools.command.develop
import setuptools.command.install
import setuptools.command.sdist
import subprocess
import sys
import textwrap
import time

# pylint is not happy with the hacks made internally by setuptools
# pylint: disable=E0611
from distutils.core import Command
from distutils.errors import DistutilsExecError
from distutils.version import LooseVersion
# pylint: enable=E0611
from setuptools import setup

# This script can run either in a source checkout (e.g., to 'setup.py sdist')
# or in an sdist tarball (to install)
MODE = 'SRC' if os.path.isdir('src') else 'SDIST'


if os.path.exists("project_config.yaml"):
    import yaml  # yaml is not standard python, so only require it for SRC mode
    pkg_cfg = yaml.load(open("project_config.yaml"))
    json.dump(pkg_cfg, open("project_config.json", "w"))
else:
    pkg_cfg = json.load(open("project_config.json"))

pkg_dir = pkg_cfg['base']['name'].replace("-", '_')
base_json = pkg_cfg['base']
package_json = pkg_cfg['node']
package_json.update(base_json)
bower_json = pkg_cfg['bower']
bower_json.update(base_json)

# command classes

cmdclass = {}


def check_output(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]


class NpmInstall(Command):
    description = "Run 'npm install' to install all of the relevant npm modules"

    user_options = []

    def initialize_options(self):
        pass

    def retrySpawn(self, cmd, retryDelay=10, numRetry=4):

        for i in xrange(numRetry):
            try:
                return self.spawn(cmd)
            except DistutilsExecError as e:
                print >> sys.stderr, e
                if i < numRetry - 1:
                    print "probably network unstability..."
                    print "retrying in %ds" % (retryDelay,)
                    time.sleep(retryDelay)
                    retryDelay *= 2

    def finalize_options(self):
        pass

    def linkToSandbox(self, d):
        if 'VIRTUAL_ENV' in os.environ:
            os.system("rm -rf %(d)s && mkdir -p $VIRTUAL_ENV/%(d)s && "
                      "ln -s $VIRTUAL_ENV/%(d)s %(d)s" % dict(d=d))

    def run(self):
        with open("package.json", "w") as f:
            json.dump(package_json, f)
        npm_version = check_output("npm -v").strip()
        if npm_version == "":
            raise RuntimeError("need nodejs and npm installed in current PATH")
        if LooseVersion(npm_version) < LooseVersion("1.2"):
            raise RuntimeError("need npm >= 1.2 (%s)" % (npm_version,))
        self.linkToSandbox('node_modules')
        self.retrySpawn(['npm', 'install'])

cmdclass['npm_install'] = NpmInstall


class BowerInstall(NpmInstall):
    description = "Run 'bower install' to install all of the relevant bower modules"

    sub_commands = [
        ('npm_install', None)
    ]

    def run(self):
        for command in self.get_sub_commands():
            self.run_command(command)
        with open("bower.json", "w") as f:
            json.dump(bower_json, f)
        self.linkToSandbox('bower_components')
        self.retrySpawn(['./node_modules/.bin/bower', 'install'])

cmdclass['bower_install'] = BowerInstall


class Grunt(Command):
    description = "Run grunt"

    user_options = [
        ('devel', 'd',
         "Do not minify JS")]

    sub_commands = [
        ('bower_install', None)
    ]

    def initialize_options(self):
        self.devel = False
        self.bindir = None

    def finalize_options(self):
        pass

    def get_bindir(self):
        if not self.bindir:
            p = subprocess.Popen(["npm", "bin"], stdout=subprocess.PIPE)
            self.bindir = p.communicate()[0].strip()
        return self.bindir

    def run(self):
        # bail out if we're not in SRC mode, since grunt won't work from
        # an sdist tarball
        if MODE != 'SRC':
            return

        for command in self.get_sub_commands():
            self.run_command(command)

        args = ['default'] if self.devel else ['prod']
        bindir = self.get_bindir()
        self.spawn([os.path.abspath(os.path.join(bindir, 'grunt'))] + args)

cmdclass['grunt'] = Grunt


class InstallWWW(Command):

    description = "install WWW files"

    user_options = [
        ('install-dir=', 'd',
         "base directory for installing WWW files "
         "(default: `$install_lib/hotfix_dashboard`)"), ]
    boolean_options = ['force']

    def initialize_options(self):
        self.install_dir = None
        self.outfiles = []

    def finalize_options(self):
        if not self.install_dir:
            cmd = self.get_finalized_command('install')
            self.install_dir = os.path.join(cmd.install_lib, pkg_dir)

    def run(self):
        out = self.copy_tree(pkg_dir, self.install_dir)
        self.outfiles.extend(out)

    def get_outputs(self):
        return self.outfiles

cmdclass['install_www'] = InstallWWW


class sdist(setuptools.command.sdist.sdist):

    """
    Customize sdist to run grunt first
    """

    def run(self):
        if MODE == 'SRC':
            self.run_command('grunt')
        # sdist is checking for os.link existance to know if it shall do hardlink
        # or copies, but there is no other way to force copies (hardlink will keep symlinks)
        # I know its ugly. I'm desesperate how setuptools and distutils are really
        # not as good as the rest of the python stdlib.
        delattr(os, "link")
        setuptools.command.sdist.sdist.run(self)

cmdclass['sdist'] = sdist


class Install(setuptools.command.install.install):

    """
    Customize install to run grunt first, and to run install_www after.
    """

    sub_commands = setuptools.command.install.install.sub_commands + [
        ('install_www', None)
    ]

    def run(self):
        if MODE == 'SRC':
            self.run_command('grunt')
        setuptools.command.install.install.run(self)

cmdclass['install'] = Install


class Develop(setuptools.command.develop.develop):

    """
    Customize develop to run npm/bower install.
    """

    sub_commands = setuptools.command.develop.develop.sub_commands + [
        ('bower_install', None),
    ]

    def run(self):
        for command in self.get_sub_commands():
            self.run_command(command)
        setuptools.command.develop.develop.run(self)

cmdclass['develop'] = Develop

entry_points = """
    [buildbot.www]
    %(pkg_dir)s = %(pkg_dir)s:ep
""" % dict(pkg_dir=pkg_dir)
if 'additional_entrypoints' in pkg_cfg['base']:
    entry_points = (textwrap.dedent(entry_points)
                    + textwrap.dedent(pkg_cfg['base']['additional_entrypoints']))
setup(
    name=pkg_cfg['base']['name'],
    version=pkg_cfg['base']['version'],
    description=pkg_cfg['base']['description'],
    author=pkg_cfg['base']['author']['name'],
    author_email=pkg_cfg['base']['author']['email'],
    url=pkg_cfg['base']['author']['url'],
    license='GNU GPL',
    packages=[str(pkg_dir)],
    cmdclass=cmdclass,
    entry_points=entry_points
)
