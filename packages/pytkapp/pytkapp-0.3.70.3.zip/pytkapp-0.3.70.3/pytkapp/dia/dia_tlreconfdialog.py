#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - dialog for tablelist reconfiguration """

# pytkapp: common dialogs - dialog for tablelist reconfiguration
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
    from tkinter import PhotoImage, Frame, Label, Checkbutton, StringVar, Canvas, Scrollbar
    from tkinter.constants import HORIZONTAL, VERTICAL, NW, N, E, W, S, SUNKEN, LEFT, RIGHT, TOP, BOTH, YES, NE, X, RAISED, SUNKEN, DISABLED, NORMAL
    from tkinter.ttk import Combobox, Notebook
    import tkinter.tkcolorchooser as tkcolorchooser
else:
    from Tkinter import PhotoImage, Frame, Label, Checkbutton, StringVar, Canvas, Scrollbar
    from Tkconstants import HORIZONTAL, VERTICAL, NW, N, E, W, S, SUNKEN, LEFT, RIGHT, TOP, BOTH, YES, NE, X, RAISED, SUNKEN, DISABLED, NORMAL
    from ttk import Combobox, Notebook
    import tkColorChooser as tkcolorchooser

# pytkapp
import pytkapp.pta_icons as pta_icons
from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
from pytkapp.pta_routines import novl, get_estr
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header, make_widget_resizeable
from pytkapp.pta_dialog import BaseDialog
from pytkapp.tkw.tkw_palentry import PalEntry

###################################
## globals
###################################
TABLELIST_ARROWSTYLES = ('flat6x4','flat7x4','flat7x5','flat7x7','flat8x5','flat9x5','flat9x6',
                         'flat9x7','flat10x6','sunken8x7','sunken10x9','sunken12x11')
TABLELIST_TREESTYLES = ('adwaita','ambiance','aqua','baghira','dust','dustSand',
                        'gtk','klearlooks','mint','newWave','oxygen1','oxygen2',
                        'phase','plastik','plastique','radiance','ubuntu',
                        'vistaAero','vistaClassic','win7Aero','win7Classic',
                        'winnative','winxpBlue','winxpOlive','winxpSilver')
TABLELIST_STYLEOPTS = ('arrowstyle', 'treestyle',)
TABLELIST_COLOROPTS = ('background', 'foreground',
                       'selectbackground', 'selectforeground',
                       'stripebackground', 'stripeforeground')
TABLELIST_CONFOPTS = TABLELIST_COLOROPTS + TABLELIST_STYLEOPTS

###################################
## routines
###################################

###################################
## classes
###################################
class TLReconfDialog(BaseDialog):
    """ sample of selector dialog """

    def __init__(self, pw_parent, **kw):
        """ init routines
        kw:
            widget - configurable tablelist
        """

        self.__colvars = []

        self.__appvars = {}

        lv_nbc = kw.get('nobackconfirm', True)
        kw['nobackconfirm'] = lv_nbc

        BaseDialog.__init__(self, pw_parent, **kw)

    def call_apply(self, po_event=None):
        """call apply conf"""

        lw_tl = self.get_kwdata('widget')
        lw_table = lw_tl.get_datawidget()

        # column
        for col_indx, col_var in enumerate(self.__colvars):
            lv_value = novl(col_var.get(), 0)

            lw_table.columnconfigure("%s" % col_indx, hide=lv_value)

        # appearance
        for appkey in tuple(self.__appvars.keys()):
            try:
                lv_key = '%s' % appkey
                lv_value = self.__appvars[appkey].get()

                if lv_value == "None":
                    lv_value = None

                ld_kw = {}
                ld_kw[lv_key] = lv_value

                lw_tl.configure(**ld_kw)
            except:
                print('%s' % get_estr())

    def call_revert_confopt(self, pv_key, pv_var, pw_ewidget, pw_twidget):
        """revert configurable options to default state"""

        lv_value = pw_twidget.get_defconfmatrix_value('^%s' % pv_key)
        if pv_key in TABLELIST_COLOROPTS:
            if lv_value is None or lv_value == '' or lv_value == "":
                lv_value = "black"
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

    def call_show_all_columns(self, po_event=None):
        """uncheck hide? state for all available columns"""

        lw_tl = self.get_kwdata('widget')
        lw_table = lw_tl.get_datawidget()

        lv_titlecols = novl(lw_table.cget('-titlecolumns'), 0)
        lv_treecol = novl(lw_table.cget('-treecolumn'), 0)

        for col_indx in range(len(self.__colvars)):
            if col_indx != 0 and col_indx != lv_treecol and col_indx >= lv_titlecols:
                self.__colvars[col_indx].set(0)

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

        lw_nb = Notebook( lw_topframe )

        # main (columns) >>>
        lw_main = Frame( lw_nb )
        lw_main.grid()
        lw_nb.add( lw_main, text=_('Columns'), padding=2 )

        lv_tr = -1

        lv_tr += 1
        lw_h = Label(lw_main, bd=1, relief=RAISED, padx=3, pady=3, bg="darkgray", text=_('Mark checkbox to hide column'), anchor=NW)
        lw_h.grid(row=lv_tr, column=0, columnspan=2, sticky=N+W+E+S, pady=2)

        lv_tr += 1
        lw_cnv = Canvas(lw_main, takefocus=1, highlightthickness=0, bd=0)
        lw_cnv.grid(row=lv_tr, column=0, sticky=N+E+W+S, padx=2, pady=2)

        lw_vscroll = Scrollbar(lw_main, orient=VERTICAL, command=lw_cnv.yview)
        lw_vscroll.grid(row=lv_tr, column=1, sticky=N+S)

        lv_tr += 1
        lw_hscroll = Scrollbar(lw_main, orient=HORIZONTAL, command=lw_cnv.xview)
        lw_hscroll.grid(row=lv_tr, column=0, sticky=W+E)

        lw_cnv.configure(yscrollcommand=lw_vscroll.set, xscrollcommand=lw_hscroll.set)

        lw_btnfrm = Frame(lw_cnv)
        lw_cnv.create_window(0, 0, window=lw_btnfrm, anchor=NW)

        lw_tl = self.get_kwdata('widget')
        lw_table = lw_tl.get_datawidget()

        lt_headers = lw_table.cget('-columntitles')
        ll_aliases = lw_tl.get_aliases()

        if not isinstance(lt_headers, tuple):
            lt_headers = tuple()

        lv_titlecols = novl(lw_table.cget('-titlecolumns'), 0)
        lv_treecol = novl(lw_table.cget('-treecolumn'), 0)

        lv_r = 0
        lt_cnfheaders = (_('Index'), _('Alias'), _('Header'), _('Hide ?'), _('Comment'))
        for hdr_indx, hdr_data in enumerate(lt_cnfheaders):
            Label(lw_btnfrm,  relief=RAISED, bd=1, text='%s' % hdr_data).grid(row=lv_r, column=hdr_indx, sticky=N+E+W+S, padx=0, pady=2)

        lv_r += 1
        for col_indx in range(len(lt_headers)):
            # prepare data
            ll_data = []
            ll_data.append(col_indx)
            try:
                lv_alias = ll_aliases[col_indx]
            except IndexError:
                lv_alias = ''
            ll_data.append(lv_alias)
            ll_data.append(lt_headers[col_indx])
            lv_hide = lw_tl.columncget("%s" % col_indx, "-hide")
            lv_var = StringVar()
            lv_var.set(lv_hide)
            self.__colvars.append(lv_var)
            ll_data.append(lv_hide)
            if col_indx == 0:
                lv_state = DISABLED
                lv_comment = _('Initial')
            elif col_indx == lv_treecol:
                lv_state = DISABLED
                lv_comment = _('Tree')
            elif col_indx < lv_titlecols:
                lv_state = DISABLED
                lv_comment = _('Fixed')
            else:
                lv_state = NORMAL
                lv_comment = ''
            ll_data.append(lv_comment)

            # display data
            for c_indx in range(len(lt_cnfheaders)):
                if c_indx in (0, len(lt_cnfheaders)-1):
                    lv_bg = None
                else:
                    lv_bg = "white"

                lv_sticky = N+E+W+S

                if c_indx == 3:
                    lw_cb = Checkbutton(lw_btnfrm, onvalue=1, offvalue=0, variable=lv_var, state=lv_state)
                    lw_cb.grid(row=lv_r, column=c_indx, sticky=lv_sticky)
                else:
                    lw_indxlab = Label(lw_btnfrm, text='%s' % ll_data[c_indx], relief=SUNKEN, bd=1, bg=lv_bg)
                    lw_indxlab.grid(row=lv_r, column=c_indx, sticky=lv_sticky)

            lv_r += 1

        lw_btn = ToolTippedBtn(lw_btnfrm, text=_('Show all'), tooltip=_('Show all available columns'), image=None, padx=10, command=self.call_show_all_columns)
        lw_btn.grid(row=lv_r, column=0, sticky=N+W+E+S, pady=2)

        # final conf
        lw_btnfrm.columnconfigure(1, weight=1)
        lw_btnfrm.columnconfigure(2, weight=1)
        lw_btnfrm.update_idletasks()

        lw_main.columnconfigure(0, weight=1)
        lw_main.rowconfigure(lv_tr-1, weight=1)
        lw_main.update_idletasks()

        lw_cnv.configure(scrollregion=(0, 0, lw_btnfrm.winfo_width(), lw_btnfrm.winfo_height()))
        # main <<<

        # appearance >>>
        lw_tabframe = Frame( lw_nb )
        lw_tabframe.grid()
        lw_nb.add( lw_tabframe, text=_('Appearance'), padding=2 )

        # start over
        lv_tr = -1

        # styles >>>
        lv_tr += 1
        lw_h = Label(lw_tabframe, bd=1, relief=RAISED, padx=3, pady=3, bg="darkgray", text=_('Change style for elements'), anchor=NW)
        lw_h.grid(row=lv_tr, column=0, columnspan=2, sticky=N+W+E+S, pady=2)

        for stylekey in TABLELIST_STYLEOPTS:
            lv_tr += 1
            lv_var = StringVar()
            lv_var.set(lw_tl.cget('-%s' % stylekey))
            lw_l = Label(lw_tabframe, text='-%s' % stylekey)
            lw_l.grid(row=lv_tr, column=0, sticky=N+W)

            if stylekey == 'treestyle':
                ll_values = TABLELIST_TREESTYLES
            elif stylekey == 'arrowstyle':
                ll_values = TABLELIST_ARROWSTYLES
            else:
                ll_values = []
            lw_cbox = Combobox(lw_tabframe,
                               state="readonly",
                               textvariable=lv_var,
                               values=ll_values)
            lw_cbox.bind('<Button-3>', lambda e=None, k=stylekey, v=lv_var, w=lw_cbox, t=lw_tl:self.call_revert_confopt(k, v, w, t))
            lw_cbox.grid(row=lv_tr, column=1, sticky=N+E+W+S)
            self.__appvars[stylekey] = lv_var

        # colors >>>
        lv_tr += 1
        lw_h = Label(lw_tabframe, bd=1, relief=RAISED, padx=3, pady=3, bg="darkgray", text=_('Double-click to select color, Right-click to revert color'), anchor=NW)
        lw_h.grid(row=lv_tr, column=0, columnspan=2, sticky=N+W+E+S, pady=2)
        for appkey in TABLELIST_COLOROPTS:
            lv_tr += 1
            lv_color = lw_tl.cget('-%s' % appkey)
            if lv_color is None or lv_color == "":
                lv_color = "black"

            lw_l = Label(lw_tabframe, text='-%s' % appkey)
            lw_l.grid(row=lv_tr, column=0, sticky=N+W)

            lw_e = PalEntry(lw_tabframe, color=lv_color)
            lw_e.grid(row=lv_tr, column=1, sticky=N+E+W+S, padx=2, pady=2)

            self.__appvars[appkey] = lw_e

        lw_tabframe.columnconfigure(1, weight=1)
        # appearance <<<

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
