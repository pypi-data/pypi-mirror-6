#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" child overviwer """

# pytkapp: child overviwer
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

if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, PhotoImage, Frame, Label
    from tkinter.constants import HORIZONTAL, NW, N, E, W, S, SUNKEN, LEFT, RIGHT, TOP, BOTH, YES, NE, X, RAISED
    from tkinter.ttk import Separator as ttkSeparator
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Tk, PhotoImage, Frame, Label
    from Tkconstants import HORIZONTAL, NW, N, E, W, S, SUNKEN, LEFT, RIGHT, TOP, BOTH, YES, NE, X, RAISED
    from ttk import Separator as ttkSeparator
    import tkMessageBox as messagebox

# pytkapp
import pytkapp.pta_icons as pta_icons
from pytkapp.pta_constants import OVERVIEWER_COEF, DEFAULT_ALPHA
from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
from pytkapp.pta_routines import novl
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header, make_widget_resizeable
from pytkapp.tkw.tkw_routines import set_widget_alpha, event_on_region, bind_children
from pytkapp.pta_dialog import BaseDialog

###################################
## globals
###################################

###################################
## routines
###################################

###################################
## classes
###################################
class ChildrenOverviewer(BaseDialog):
    """ overview children """

    def __init__(self, pw_parent, **kw):
        """ init routines """

        self.__result = None

        kw['nobackconfirm'] = True
        kw['title'] = _('Children')

        lv_nbc = kw.get('nobackconfirm', True)
        kw['nobackconfirm'] = lv_nbc

        self.__active = kw['active']
        self.__family = kw['family']
        self.__btns = []

        BaseDialog.__init__(self, pw_parent, **kw)

    def on_select(self, pv_result=None):
        """ set result on select """

        self.__result = pv_result
        self.get_toplevel().destroy()

    def on_leave(self, po_event=None):
        """check event and destroy if really leave"""

        if not event_on_region(self.get_toplevel(), po_event):
            self.call_back()

        return "break"

    def show(self, **kw):
        """ show routines """

        lw_toplevel, lw_topframe = toplevel_header(self.get_parent(),
                                                   title=self.get_kwtitle(),
                                                   path=self.get_kwlogopath(),
                                                   logo=self.get_kwlogoname(),
                                                   destroycmd=self.call_back,
                                                   noresize=1
                                                  )
        self.set_toplevel(lw_toplevel)

        lw_toplevel.configure(padx=10, pady=10, bg="dark gray")
        lw_topframe.configure(bg="dark gray")

        set_widget_alpha(lw_toplevel, DEFAULT_ALPHA)

        lv_familysize = len(self.__family)
        lv_x = int(round(lv_familysize ** OVERVIEWER_COEF))

        lv_r   = 0
        lv_c   = 0

        lv_activebtn = None

        for child_key, child_data in self.__family:
            lv_childid = child_key
            lv_childtitle = child_data.get_title()
            lv_childdesc = child_data.get_description()
            lv_childclass = child_data.get_classname()

            lw_image = child_data.get_resource_item('child_logo')

            if lv_childid == self.__active:
                lv_relief = SUNKEN
            else:
                lv_relief = RAISED

            lv_tooltip = _('Title:\n%s\nStatuses:\n(1): %s\n(2): %s\n(3): %s') % (lv_childtitle, lv_childdesc[0], lv_childdesc[1], lv_childdesc[2],)

            lw_btn = ToolTippedBtn(lw_topframe,
                                   tooltip = lv_tooltip,
                                   image = lw_image,
                                   text = '%s %s' % (lv_childclass, lv_childid,),
                                   compound = LEFT,
                                   relief = lv_relief,
                                   command=lambda ev=None, chid=lv_childid: self.on_select(chid)
                                   )
            lw_btn.grid(row=lv_r, column=lv_c, padx=2, pady=2, sticky=N+E+W+S)
            self.__btns.append(lw_btn)

            if lv_childid == self.__active:
                lv_activebtn = lw_btn

            if lv_c >= lv_x-1:
                lv_c = 0
                lv_r += 1
            else:
                lv_c += 1

        # set one size for all buttons
        lv_maxwidth  = max([btn.winfo_reqwidth() for btn in self.__btns])
        lv_maxheight = max([btn.winfo_reqheight() for btn in self.__btns])
        lv_maxsize   = max(lv_maxwidth, lv_maxheight)

        for btn in self.__btns:
            btn.configure(width=lv_maxsize, height=lv_maxsize)

        make_widget_resizeable(lw_toplevel)
        lw_toplevel.update_idletasks()

        scrW = lw_toplevel.winfo_screenwidth()
        scrH = lw_toplevel.winfo_screenheight()

        lw_toplevel.update_idletasks()
        reqW = lw_toplevel.winfo_reqwidth()
        reqH = lw_toplevel.winfo_reqheight()

        Xpos = (scrW - reqW) // 2
        Ypos = (scrH - reqH) // 2

        lw_parent = self.get_parent()

        #lw_toplevel.overrideredirect(True)
        lw_toplevel.geometry(str(reqW)+"x"+str(reqH)+"+"+str(Xpos)+"+"+str(Ypos))
        lw_toplevel.resizable(width=False, height=False)

        if lv_activebtn:
            lv_activebtn.focus_set()

        lw_toplevel.grab_set()

        bind_children(lw_toplevel, '<Leave>', self.on_leave, '+')

        lw_toplevel.deiconify()
        lw_toplevel.lift()

        lw_parent.wait_window(lw_toplevel)

        # return selected child id
        return self.__result
