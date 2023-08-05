#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tkinter classes and constants"""

# pytkapp: application base class
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
## import
###################################
import sys

if sys.hexversion >= 0x03000000:
    #from pytkapp.cpr.py3tkinter import *

    from pytkapp.cpr.py3tkinter import cpr_tkinter as cpr_tkinter
    from pytkapp.cpr.py3tkinter import cpr_tkconstants as cpr_tkconstants
    
    from pytkapp.cpr.py3tkinter import cpr_tkscrolledtext as cpr_tkscrolledtext
    from pytkapp.cpr.py3tkinter import cpr_tkcolorchooser as cpr_tkcolorchooser
    from pytkapp.cpr.py3tkinter import cpr_tkcommondialog as cpr_tkcommondialog
    from pytkapp.cpr.py3tkinter import cpr_tkfiledialog as cpr_tkfiledialog
    from pytkapp.cpr.py3tkinter import cpr_tkfont as cpr_tkfont
    from pytkapp.cpr.py3tkinter import cpr_tkmessagebox as cpr_tkmessagebox
    from pytkapp.cpr.py3tkinter import cpr_tksimpledialog as cpr_tksimpledialog
    from pytkapp.cpr.py3tkinter import cpr_ttk as cpr_ttk    
else:
    #from pytkapp.cpr.py2tkinter import *
    
    from pytkapp.cpr.py2tkinter import cpr_tkinter as cpr_tkinter
    from pytkapp.cpr.py2tkinter import cpr_tkconstants as cpr_tkconstants
    
    from pytkapp.cpr.py2tkinter import cpr_tkscrolledtext as cpr_tkscrolledtext
    from pytkapp.cpr.py2tkinter import cpr_tkcolorchooser as cpr_tkcolorchooser
    from pytkapp.cpr.py2tkinter import cpr_tkcommondialog as cpr_tkcommondialog
    from pytkapp.cpr.py2tkinter import cpr_tkfiledialog as cpr_tkfiledialog
    from pytkapp.cpr.py2tkinter import cpr_tkfont as cpr_tkfont
    from pytkapp.cpr.py2tkinter import cpr_tkmessagebox as cpr_tkmessagebox
    from pytkapp.cpr.py2tkinter import cpr_tksimpledialog as cpr_tksimpledialog
    from pytkapp.cpr.py2tkinter import cpr_ttk as cpr_ttk
       
# FIXME: is it correct way ?
# direct add to modules >>>
sys.modules['cpr_tkinter'] = cpr_tkinter
sys.modules['cpr_tkconstants'] = cpr_tkconstants

sys.modules['cpr_tkscrolledtext'] = cpr_tkscrolledtext
sys.modules['cpr_tkcolorchooser'] = cpr_tkcolorchooser
sys.modules['cpr_tkcommondialog'] = cpr_tkcommondialog
sys.modules['cpr_tkfiledialog'] = cpr_tkfiledialog
sys.modules['cpr_tkfont'] = cpr_tkfont
sys.modules['cpr_tkmessagebox'] = cpr_tkmessagebox
sys.modules['cpr_tksimpledialog'] = cpr_tksimpledialog
sys.modules['cpr_ttk'] = cpr_ttk