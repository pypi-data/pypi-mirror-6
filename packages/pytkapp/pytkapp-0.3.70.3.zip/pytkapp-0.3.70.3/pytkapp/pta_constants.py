#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common constants """

# pytkapp: common constants
#
# Copyright (c) 2013 Paul "Mid.Tier"
# Author e-mail: mid.tier@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

###################################
## constants
###################################
MAGIC_W2L = 0.55
MAGIC_W_RES = 640
MAGIC_H_RES = 480

APP_MAX_CHILDREN = 50
APP_MAX_SUBCHILDREN = 5

APP_RECENTLIST_LEN = 10

APP_UI_MODE_MDI = 'mdi'
APP_UI_MODE_SDI = 'sdi'
APP_UI_MODE_CLI = 'cli'
APP_UI_MODE_BAT = 'bat'

CHILD_UI_MODE_MDI = 'onefromcrowd'
CHILD_UI_MODE_SDI = 'single'
CHILD_UI_MODE_CLI = 'casper'

CHILD_ACTIVE = 'active'
CHILD_BUSY = 'busy'
CHILD_INACTIVE = 'inactive'

LOG_WSTATE_NORMAL = 'normal'
LOG_WSTATE_HIDDEN = 'hidden'

OVERVIEWER_COEF = 0.5

DEFAULT_ALPHA = 0.8

CHILD_WSTATE_NORMAL = 0
CHILD_WSTATE_MAXIMIZED = 1