#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" expandable toolbar container """

# pytkapp.tkw: expandable toolbar container
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

import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if sys.hexversion >= 0x03000000:
    from tkinter import Tk, Frame
    from tkinter.constants import N, S, W, E, LEFT, TOP, X, SUNKEN
    from tkinter.constants import SUNKEN
else:
    from Tkinter import Tk, Frame
    from Tkconstants import N, S, W, E, LEFT, TOP, X, SUNKEN
    from Tkconstants import SUNKEN

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

# pytkapp
from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
import pytkapp.tkw.tkw_icons as tkw_icons

###################################
## classes
###################################
class ToolbarGroup(Frame):
    """expandable toolbar container"""

    def __init__( self, master, **kw ):
        """init widget"""

        if kw.has_key('toolgroupname'):
            self._tgname = kw.pop('toolgroupname')
        else:
            self._tgname = None

        Frame.__init__(self, master, **kw)

        self.__mainframe = Frame(self, bd=1, takefocus=0, pady=2)
        self.__mainframe.grid(row=0, column=0, sticky=N+E+W+S, padx=1)

        self.__supportframe = Frame(self, bd=1, takefocus=0, relief=SUNKEN, bg="gray", padx=2, pady=2)
        self.__supportframe.grid(row=0, column=1, sticky=N+E+W+S, padx=1)

        self.__ctrlbtn = ToolTippedBtn(self)
        self.__ctrlbtn.grid(row=0, column=2, sticky=N+E+W+S, padx=1)
        self.__ctrlbtn.grid_propagate()

        # prepare collapse
        self.collapse_group()

    def get_mainframe(self):
        """return main frame"""

        return self.__mainframe

    def get_supportframe(self):
        """return support frame"""

        return self.__supportframe

    def call_expand_group(self, po_event=None):
        """call expand"""

        self.expand_group()

    def expand_group(self):
        """expand group"""

        self.__supportframe.grid(row=0, column=1, sticky=N+E+W+S, padx=1)
        if self._tgname:
            lv_tooltip = _('Collapse "%s"') % self._tgname
        else:
            lv_tooltip = _('Collapse group')
        self.__ctrlbtn.configure(image=tkw_icons.get_icon('gv_icon_toolgroup_collapse'), tooltip=lv_tooltip, command=self.call_collapse_group)

    def call_collapse_group(self, po_event=None):
        """call collapse"""

        self.collapse_group()

    def collapse_group(self):
        """collapse"""

        self.__supportframe.grid_forget()
        if self._tgname:
            lv_tooltip = _('Expand "%s"') % self._tgname
        else:
            lv_tooltip = _('Expand group')
        self.__ctrlbtn.configure(image=tkw_icons.get_icon('gv_icon_toolgroup_expand'), tooltip=lv_tooltip, command=self.call_expand_group)


def run_demo():
    """main demo"""

    root = Tk()

    frm = Frame(root)

    group = ToolbarGroup(frm, toolgroupname='Custom name')

    # create buttons for main frame
    mf = group.get_mainframe()
    for i in range(1, 4):
        b = ToolTippedBtn(mf, text='B%s' % i, tooltip='Button %s' % i)
        b.pack(side=LEFT)

    # create buttons for support frame
    sf = group.get_supportframe()
    for i in range(1, 4):
        b = ToolTippedBtn(sf, text='(s) B%s' % i, tooltip='(s) Button %s' % i)
        b.pack(side=LEFT)

    group.pack(side=TOP, fill=X)

    frm.pack()

    root.mainloop()

if __name__ == '__main__':
    run_demo()