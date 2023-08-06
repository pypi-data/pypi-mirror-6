#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011, 2012, 2013, 2014 Jérôme Poisson <goffi@goffi.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distribute_setup import use_setuptools
use_setuptools()
from setuptools.command.install import install
from setuptools import setup
from distutils.file_util import copy_file
import os
import sys
import subprocess
from stat import ST_MODE

# seen here: http://stackoverflow.com/questions/7275295
try:
    from setuptools.command import egg_info
    egg_info.write_toplevel_names
except (ImportError, AttributeError):
    pass
else:
    def _top_level_package(name):
        return name.split('.', 1)[0]

    def _hacked_write_toplevel_names(cmd, basename, filename):
        pkgs = dict.fromkeys(
            [_top_level_package(k)
                for k in cmd.distribution.iter_distribution_names()
                if _top_level_package(k) != "twisted"
            ]
        )
        cmd.write_file("top-level names", filename, '\n'.join(pkgs) + '\n')

    egg_info.write_toplevel_names = _hacked_write_toplevel_names


NAME = 'libervia'
LAUNCH_DAEMON_COMMAND = 'libervia'


class MercurialException(Exception):
    pass


def module_installed(module_name):
    """Try to import module_name, and return False if it failed
    @param module_name: name of the module to test
    @return: True if successful"""
    try:
        __import__(module_name)
    except ImportError:
        return False
    return True


class CustomInstall(install):

    def custom_auto_options(self):
        """Change options for twistd in the shell script
        Mainly change the paths"""
        sh_buffer = ""
        run_dir = os.path.dirname(self.sh_script_path)
        with open(self.sh_script_path, 'r') as sh_file:
            for ori_line in sh_file:
                if ori_line.startswith('DAEMON='):
                    dest_line = 'DAEMON=""\n'  # we want to launch sat as a daemon
                elif ori_line.startswith('TAP_PATH='):
                    dest_line = 'TAP_PATH="%s/"\n' % run_dir
                elif ori_line.startswith('PYTHON='):
                    dest_line = 'PYTHON="%s"\n' % sys.executable
                else:
                    dest_line = ori_line
                sh_buffer += dest_line

        with open(self.sh_script_path, 'w') as sh_file:
            sh_file.write(sh_buffer)

    def custom_create_links(self):
        """Create symbolic links to executables"""
        # the script which launch the daemon
        links = [(self.sh_script_path, LAUNCH_DAEMON_COMMAND)]
        for source, dest in links:
            dest_name, copied = copy_file(source, os.path.join(self.install_scripts, dest), link='sym')
            assert (copied)
            # we change the perm in the same way as in the original install_scripts
            mode = ((os.stat(dest_name)[ST_MODE]) | 0555) & 07777
            os.chmod(dest_name, mode)

    def pyjs_build(self):
        return subprocess.call('pyjsbuild libervia --no-compile-inplace -m -I %s' % self.install_lib, shell=True)

    def run(self):
        sys.stdout.write('running pre installation stuff\n')
        sys.stdout.flush()
        build_result = self.pyjs_build()
        if build_result == 127:  # TODO: remove magic string
            print "pyjsbuild is not installed or not accessible from the PATH of user '%s'" % os.getenv('USERNAME')
            return
        if build_result != 0:
            print "pyjsbuild failed to build libervia"
            return
        install.run(self)
        sys.stdout.write('running post installation stuff\n')
        sys.stdout.flush()
        self.sh_script_path = os.path.join(self.install_lib, 'libervia_server', 'libervia.sh')
        self.custom_auto_options()
        self.custom_create_links()


def preinstall_check():
    """Check presence of problematic dependencies, and try to install them with package manager
    This ugly stuff is necessary as distributions are not installed correctly with setuptools/distribute
    Hope to remove this at some point"""

    modules_tocheck = []  # if empty this method is dummy

    package = {'twisted': 'python-twisted-core',
               'twisted.words': 'python-twisted-words',
               'twisted.web': 'python-twisted-web',
               'mercurial': 'mercurial'}  # this dict map dependencies to packages names for debian distributions

    sys.stdout.write("Running pre-installation dependencies check\n")

    # which modules are not installed ?
    modules_toinstall = [mod for mod in modules_tocheck if not module_installed(mod)]

    if modules_toinstall:
        # are we on a distribution using apt ?
        apt_path = subprocess.Popen('which apt-get', stdout=subprocess.PIPE, shell=True).communicate()[0][:-1]
        not_installed = set()
        if apt_path:
            # we have apt, we'll try to use it
            for module_name in modules_toinstall:
                package_name = package[module_name]
                sys.stdout.write("Installing %s\n" % package_name)
                success = subprocess.call('%s -qy install %s' % (apt_path, package_name), shell=True) == 0
                if not success:
                    not_installed.add(module_name)
        else:
            not_installed = set(modules_toinstall)

        if not_installed:
            # some packages can't be automatically installed, we print their name for manual installation
            sys.stdout.write("You should install the following dependencies with your distribution recommanded tool before installing %s:\n" % NAME)
            for module_name in not_installed:
                sys.stdout.write("- %s (Debian name: %s)\n" % (module_name, package[module_name]))
            sys.exit(2)


if sys.argv[1].lower() in ['egg_info', 'install']:
    # we only check dependencies if egg_info or install is used
    install_opt = os.environ.get("LIBERVIA_INSTALL", "")
    if not "nopreinstall" in install_opt:  # user can force preinstall skipping
        preinstall_check()

setup(name=NAME,
      version='0.4.0',
      description=u'Web frontend for Salut à Toi',
      long_description=u'Libervia is a web frontend for Salut à Toi (SàT), a multi-frontends and multi-purposes XMPP client.',
      author='Goffi (Jérôme Poisson)',
      author_email='goffi@goffi.org',
      url='http://sat.goffi.org',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Twisted',
                   'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
                   'Operating System :: POSIX :: Linux',
                   'Topic :: Communications :: Chat'],
      package_dir={'libervia': '.', 'libervia_server': 'libervia_server'},
      packages=['libervia', 'libervia.output', 'libervia_server', 'twisted.plugins'],
      package_data={'libervia': ['libervia.py'], 'libervia.output': ['**/*.*'], 'libervia_server': ['libervia.sh']},
      data_files=[('share/doc/%s' % NAME, ['COPYING', 'README'])],
      scripts=[],
      zip_safe=False,
      dependency_links=['http://www.blarg.net/%7Esteveha/pyfeed-0.7.4.tar.gz', 'http://www.blarg.net/%7Esteveha/xe-0.7.4.tar.gz'],
      install_requires=['sat', 'twisted', 'pyfeed', 'xe', 'txjsonrpc', 'zope'],
      cmdclass={'install': CustomInstall},
      )

