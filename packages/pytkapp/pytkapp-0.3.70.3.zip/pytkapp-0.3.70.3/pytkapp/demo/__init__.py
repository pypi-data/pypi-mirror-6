#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Dummy file to make this directory a package """

# dummy file
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

import sys
import os.path

try:
    sys.path.append(__path__[0])
except:
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), 'demo'))