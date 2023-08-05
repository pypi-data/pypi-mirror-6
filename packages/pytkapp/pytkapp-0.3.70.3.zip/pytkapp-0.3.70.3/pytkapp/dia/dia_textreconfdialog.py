#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - dialog for xscrolled reconfiguration """

# pytkapp: common dialogs - dialog for xscrolled reconfiguration
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
    from tkinter import PhotoImage, Frame, Entry, Label, Checkbutton, StringVar, Canvas, Scrollbar
    from tkinter.constants import HORIZONTAL, VERTICAL, NW, N, E, W, S, SUNKEN, LEFT, RIGHT, TOP, BOTH, YES, NE, X, RAISED, SUNKEN, DISABLED, NORMAL, CENTER
    from tkinter.ttk import Combobox, Notebook
    import tkinter.tkcolorchooser as tkcolorchooser
else:
    from Tkinter import PhotoImage, Frame, Entry, Label, Checkbutton, StringVar, Canvas, Scrollbar
    from Tkconstants import HORIZONTAL, VERTICAL, NW, N, E, W, S, SUNKEN, LEFT, RIGHT, TOP, BOTH, YES, NE, X, RAISED, SUNKEN, DISABLED, NORMAL, CENTER
    from ttk import Combobox, Notebook
    import tkColorChooser as tkcolorchooser

# pytkapp
import pytkapp.pta_icons as pta_icons
from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
from pytkapp.pta_routines import novl, get_estr
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header, make_widget_resizeable, make_widget_ro
from pytkapp.pta_dialog import BaseDialog
from pytkapp.tkw.tkw_palentry import PalEntry

###################################
## globals
###################################
XSCROLLEDTEXT_COLOROPTS = ('background', 'foreground',
                           'insertbackground',
                           'selectbackground', 'selectforeground',)

XSCROLLEDTEXT_TAGS = ('info', 'warning', 'error', 'ask',)

XSCROLLEDTEXT_CONFOPTS = XSCROLLEDTEXT_COLOROPTS

###################################
## routines
###################################

###################################
## classes
###################################
class TextReconfDialog(BaseDialog):
    """ sample of selector dialog """

    def __init__(self, pw_parent, **kw):
        """ init routines
        kw:
            widget - configurable xscrolledtext
        """

        self.__colvars = []

        self.__appvars = {}

        lv_nbc = kw.get('nobackconfirm', True)
        kw['nobackconfirm'] = lv_nbc

        BaseDialog.__init__(self, pw_parent, **kw)

    def call_apply(self, po_event=None):
        """call apply conf"""

        lw_widget = self.get_kwdata('widget')
        lw_text = lw_widget.get_datawidget()

        # appearance
        for appkey in XSCROLLEDTEXT_COLOROPTS:
            try:
                lv_key = '%s' % appkey
                lv_value = self.__appvars[appkey].get()

                if lv_value == "None":
                    lv_value = None

                ld_kw = {}
                ld_kw[lv_key] = lv_value

                lw_text.configure(**ld_kw)
            except:
                print('%s' % get_estr())

        # tags
        for tagkey in lw_widget.get_palette():
            try:
                lv_key = '%s' % tagkey
                lv_value = self.__appvars[tagkey].get()

                if lv_value == "None":
                    lv_value = None

                lw_widget.set_palette_color(tagkey, lv_value)
            except:
                print('%s' % get_estr())

        lw_widget.apply_palette()

    def call_revert_confopt(self, pv_key, pv_var, pw_ewidget, pw_twidget):
        """revert configurable options to default state"""

        if pv_key in XSCROLLEDTEXT_COLOROPTS:
            lv_value = pw_twidget.get_defconfmatrix_value('^%s' % pv_key)

            if lv_value is None or lv_value == '' or lv_value == "":
                lv_value = "black"
            pw_ewidget.configure(bg=lv_value, insertbackground=lv_value)
        elif pv_key in pw_twidget.get_palette():
            lv_value = pw_twidget.get_defconfmatrix_value('@%s' % pv_key)

            if lv_value is None or lv_value == '' or lv_value == "":
                lv_value = pw_twidget.get_defpalette_color('mark')

            pw_ewidget.configure(bg=lv_value, insertbackground=lv_value)

        pv_var.set(lv_value)

    def call_select_color(self, pv_key, pv_var, pw_widget):
        """select color"""

        lv_color = pw_widget.cget('background')
        lv_rgb, lv_hex = tkcolorchooser.askcolor(color=lv_color,
                                                 title=_('Select color for "-%s"' % pv_key),
                                                 parent=self.get_mcontainer())
        pw_widget.configure(bg=lv_hex, insertbackground=lv_hex)
        pv_var.set(lv_hex)

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

        lw_widget = self.get_kwdata('widget')
        lw_text = lw_widget.get_datawidget()

        lw_nb = Notebook( lw_topframe )

        # appearance >>>
        lw_tabframe = Frame( lw_nb )
        lw_tabframe.grid()
        lw_nb.add( lw_tabframe, text=_('Appearance'), padding=2 )

        # start over
        lv_tr = -1

        # colors >>>
        lv_tr += 1
        lw_h = Label(lw_tabframe, bd=1, relief=RAISED, padx=3, pady=3, bg="darkgray", text=_('Double-click to select color, Right-click to revert color'), anchor=NW)
        lw_h.grid(row=lv_tr, column=0, columnspan=2, sticky=N+W+E+S, pady=2)
        for appkey in XSCROLLEDTEXT_COLOROPTS:
            lv_tr += 1
            lv_color = lw_text.cget('%s' % appkey)
            if lv_color is None or lv_color == "":
                lv_color = "black"

            lw_l = Label(lw_tabframe, text='-%s' % appkey)
            lw_l.grid(row=lv_tr, column=0, sticky=N+W)

            lw_e = PalEntry(lw_tabframe, color=lv_color)
            lw_e.grid(row=lv_tr, column=1, sticky=N+E+W+S, padx=2, pady=2)

            self.__appvars[appkey] = lw_e

        lw_tabframe.columnconfigure(1, weight=1)
        # appearance <<<

        # tags >>>
        lw_tabframe = Frame( lw_nb )
        lw_tabframe.grid()
        lw_nb.add( lw_tabframe, text=_('Tags'), padding=2 )

        # start over
        lv_tr = -1

        # default >>>
        lv_tr += 1
        lw_h = Label(lw_tabframe, bd=1, relief=RAISED, padx=3, pady=3, bg="darkgray", text=_('Double-click to select color, Right-click to revert color'), anchor=NW)
        lw_h.grid(row=lv_tr, column=0, columnspan=2, sticky=N+W+E+S, pady=2)
        for tagkey in XSCROLLEDTEXT_TAGS:
            lv_tr += 1
            lv_color = lw_widget.get_palette_color(tagkey)
            if lv_color is None or lv_color == "":
                lv_color = "black"

            lw_l = Label(lw_tabframe, text='@%s' % tagkey)
            lw_l.grid(row=lv_tr, column=0, sticky=N+W)

            lw_e = PalEntry(lw_tabframe, color=lv_color)
            lw_e.grid(row=lv_tr, column=1, sticky=N+E+W+S, padx=2, pady=2)

            self.__appvars[tagkey] = lw_e

        # others >>>
        ll_othtags = sorted([tagkey for tagkey in lw_widget.get_palette() if tagkey not in XSCROLLEDTEXT_TAGS])
        if ll_othtags:
            lv_tr += 1
            lw_h = Label(lw_tabframe, bd=1, relief=RAISED, padx=3, pady=3, bg="darkgray", text=_('Double-click to select color, Right-click to revert color'), anchor=NW)
            lw_h.grid(row=lv_tr, column=0, columnspan=2, sticky=N+W+E+S, pady=2)
            for tagkey in ll_othtags:
                lv_tr += 1
                lv_color = lw_widget.get_palette_color(tagkey)
                if lv_color is None or lv_color == "":
                    lv_color = "black"

                lw_l = Label(lw_tabframe, text='%s' % tagkey)
                lw_l.grid(row=lv_tr, column=0, sticky=N+W)

                lw_e = PalEntry(lw_tabframe, color=lv_color)
                lw_e.grid(row=lv_tr, column=1, sticky=N+E+W+S, padx=2, pady=2)

                self.__appvars[tagkey] = lw_e

        lw_tabframe.columnconfigure(1, weight=1)
        # tags <<<

        lw_nb.pack(side=TOP, fill=BOTH, expand=YES, padx=2, pady=2)

        # controls >>>
        lw_cframe = Frame(lw_topframe, relief=RAISED, bd=2)

        img = PhotoImage(data=pta_icons.get_icon('gv_icon_action_check'))
        lw_savebtn = ToolTippedBtn(lw_cframe, image=img, tooltip=_('Apply'), command=self.call_apply)
        lw_savebtn.pack(side=LEFT, anchor=NW, padx=2, pady=2)

        img = PhotoImage(data=pta_icons.get_icon('gv_app_action_back'))
        lw_backbtn = ToolTippedBtn(lw_cframe, image=img, tooltip=_('Back'), command=self.call_back)
        lw_backbtn.pack(side=RIGHT, anchor=NE, padx=2, pady=2)

        lw_cframe.pack(side=TOP, fill=X)

        make_widget_resizeable(lw_toplevel)
        lw_toplevel.update_idletasks()

        toplevel_footer(lw_toplevel,
                        self.get_parent(),
                        min_width=max(lw_toplevel.winfo_reqwidth(), kw.get('width',150)),
                        min_height=max(lw_toplevel.winfo_reqheight(), kw.get('height',100)),
                        hres_allowed=kw.get('hal',False),
                        wres_allowed=kw.get('wal',False)
                        )
