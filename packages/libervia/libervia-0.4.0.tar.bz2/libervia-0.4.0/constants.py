#!/usr/bin/python
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014 Jérôme Poisson (goffi@goffi.org)

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

from sat.core.i18n import _, D_
from sat_frontends import constants


class Const(constants.Const):

    APP_NAME = 'Libervia'

    TIMEOUT = 300  # Session's time out, after that the user will be disconnected
    LIBERVIA_DIR = "output/"
    MEDIA_DIR = "media/"
    AVATARS_DIR = "avatars/"
    CARDS_DIR = "games/cards/tarot"

    ERRNUM_BRIDGE_ERRBACK = 0  # FIXME
    ERRNUM_LIBERVIA = 0  # FIXME

    # Security limit for Libervia (get/set params)
    SECURITY_LIMIT = 5

    # Security limit for Libervia server_side
    SERVER_SECURITY_LIMIT = constants.Const.NO_SECURITY_LIMIT

    # Frontend parameters
    ENABLE_UNIBOX_KEY = D_("Composition")
    ENABLE_UNIBOX_PARAM = D_("Enable unibox")
