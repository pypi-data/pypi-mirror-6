#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2013  Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>

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

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from xdg.BaseDirectory import save_config_path
from ConfigParser import SafeConfigParser, NoSectionError
from os.path import expanduser

try:
    from libervia_server import Libervia
except (ImportError, SystemExit):
    pass  # avoid raising an error when you call twisted and sat is not launched


class Options(usage.Options):
    optParameters = [['port', 'p', 8080, 'The port number to listen on.']]


class LiberviaMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = 'libervia'
    description = 'The web frontend of Salut à Toi'
    options = Options

    def makeService(self, options):
        if not isinstance(options['port'], int):
            port = int(options['port'])
        else:
            try:
                port = config.getint('libervia', 'port')
            except NoSectionError:
                port = 8080
        return Libervia(port=port)


config_path = save_config_path('sat')
config = SafeConfigParser()
config.read(map(expanduser, ['/etc/sat.conf', config_path + '/sat.conf', 'sat.conf', '.sat.conf']))

serviceMaker = LiberviaMaker()
