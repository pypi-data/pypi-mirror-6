#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - notebooked selector """

# pytkapp: common dialogs - notebooked selector
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
import itertools
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
    from tkinter.ttk import Notebook
else:
    from Tkinter import Tk, PhotoImage, Frame, Label
    from Tkconstants import HORIZONTAL, NW, N, E, W, S, SUNKEN, LEFT, RIGHT, TOP, BOTH, YES, NE, X, RAISED
    from ttk import Separator as ttkSeparator
    import tkMessageBox as messagebox
    from ttk import Notebook

# pytkapp
import pytkapp.pta_icons as pta_icons
from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
from pytkapp.pta_routines import novl
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header, make_widget_resizeable
from pytkapp.pta_dialog import BaseDialog

###################################
## globals
###################################
VARIANT_ITEMS = 5

###################################
## routines
###################################

###################################
## classes
###################################
class BaseNBSelector(BaseDialog):
    """ sample of selector dialog """

    def __init__(self, pw_parent, **kw):
        """ init routines """

        self.__result = None

        lv_nbc = kw.get('nobackconfirm', True)
        kw['nobackconfirm'] = lv_nbc

        BaseDialog.__init__(self, pw_parent, **kw)

    def on_select(self, pv_result=None):
        """ set result on select """

        self.__result = pv_result
        self.get_toplevel().destroy()

    def show(self, **kw):
        """ show routines """

        ll_variantdata = self.get_kwdata('variants', [])

        # correct variants
        for vindx, vdata in enumerate(ll_variantdata):
            ll_empty = list(itertools.repeat('', VARIANT_ITEMS))

            for vsubindx, vsubdata in enumerate(vdata[:min(len(vdata), VARIANT_ITEMS)]):
                ll_empty[vsubindx] = vsubdata

            ll_variantdata[vindx] = ll_empty

        lv_varlen = len(ll_variantdata)

        # if get only one variant - show simple ok/cancel dialog
        if lv_varlen == 0:
            self.__result = None
        elif lv_varlen == 1:
            variant_data = ll_variantdata[0]
            lv_text = variant_data[1]
            if lv_text != '<separator>':
                lv_tooltip = novl(variant_data[2], lv_text)
                lv_answer = novl(variant_data[4], lv_text)

                self.__result = lv_answer if messagebox.askokcancel(_('Confirm'),
                                                                    _('Variant: %s') % lv_text,
                                                                    detail=lv_tooltip,
                                                                    parent=self.get_parent()) else None
            else:
                self.__result = None
        else:
            lw_toplevel, lw_topframe = toplevel_header(self.get_parent(),
                                                       title=self.get_kwtitle(),
                                                       path=self.get_kwlogopath(),
                                                       logo=self.get_kwlogoname(),
                                                       destroycmd=self.call_back,
                                                       noresize=1
                                                      )
            self.set_toplevel(lw_toplevel)

            # main >>>
            lw_main = Frame(lw_topframe, relief=SUNKEN, bd=2)

            lv_r = 0
            lv_detail = self.get_kwdata('detail', None)
            if lv_detail is not None:
                lw_label = Label(lw_main, text=lv_detail, anchor=NW, justify=LEFT)
                lw_label.grid(row=lv_r, column=0, sticky=N+E+W+S, padx=2, pady=2)
                lv_r += 1

            lv_initialfocus = self.get_kwdata('focusindx', 0)

            lw_nb = Notebook( lw_main )

            # store list [frame used for tab, last used row]
            ld_nbs = {}

            for varind, variant_data in enumerate(ll_variantdata):
                lv_tabname = variant_data[0]

                if lv_tabname not in ld_nbs:
                    lw_tabframe = Frame(lw_nb)
                    lw_tabframe.grid()
                    lw_tabframe.columnconfigure(0, weight=1)

                    lw_nb.add( lw_tabframe, text=_(lv_tabname), padding=2 )
                    lv_tr = 0
                    ld_nbs[lv_tabname] = [lw_tabframe, lv_tr]
                else:
                    lw_tabframe, lv_tr = ld_nbs[lv_tabname]

                lv_text = variant_data[1]

                if lv_text != '<separator>':
                    lv_tooltip = novl(variant_data[2], lv_text)
                    lv_icon = variant_data[3]
                    lf_command = lambda ev = None, v = novl(variant_data[4], lv_text): self.on_select(v)

                    if lv_icon is not None:
                        lo_image = PhotoImage(data=lv_icon)
                    else:
                        lo_image = None

                    lw_item = ToolTippedBtn(lw_tabframe,
                                            text=lv_text,
                                            tooltip=lv_tooltip,
                                            image=lo_image,
                                            command=lf_command,
                                            compound=LEFT,
                                            justify=LEFT,
                                            anchor=NW,
                                            takefocus=1
                                            )
                    lw_item.grid(row=lv_tr, column=0, sticky=N+E+W, pady=2, padx=2)

                    if lv_initialfocus == varind:
                        lw_item.focus_set()
                else:
                    lw_item = ttkSeparator(lw_tabframe, orient=HORIZONTAL)
                    lw_item.grid(row=lv_tr, column=0, sticky=N+E+W, pady=5, padx=2)

                ld_nbs[lv_tabname][1] = lv_tr+1

            lw_nb.grid(row=lv_r, column=0, sticky=N+E+W+S, padx=2, pady=2)
            lw_nb.columnconfigure(0, weight=1)
            lw_nb.rowconfigure(0, weight=1)

            #####################################
            #for varind, variant_data in enumerate(ll_variantdata):
                #lv_text = variant_data[0]

                #if lv_text != '<separator>':
                    #lv_tooltip = novl(variant_data[1], lv_text)
                    #lv_icon = variant_data[2]
                    #lf_command = lambda ev = None, v = novl(variant_data[3], lv_text): self.on_select(v)

                    #if lv_icon is not None:
                        #lo_image = PhotoImage(data=lv_icon)
                    #else:
                        #lo_image = None
                    #lw_item = ToolTippedBtn(lw_main,
                                            #text=lv_text,
                                            #tooltip=lv_tooltip,
                                            #image=lo_image,
                                            #command=lf_command,
                                            #compound=LEFT,
                                            #justify=LEFT,
                                            #anchor=NW,
                                            #takefocus=1
                                            #)
                    #lw_item.grid(row=lv_r, column=0, sticky=N+E+W, pady=2, padx=2)

                    #if lv_initialfocus == varind:
                        #lw_item.focus_set()
                #else:
                    #lw_item = ttkSeparator(lw_main, orient=HORIZONTAL)
                    #lw_item.grid(row=lv_r, column=0, sticky=N+E+W, pady=5, padx=2)

                #lv_r += 1

            lw_main.columnconfigure(0, weight=1)
            # should be row with notebook
            lw_main.rowconfigure(lv_r, weight=1)

            lw_main.pack(side=TOP, fill=BOTH, expand=YES, padx=2, pady=2)

            # controls >>>
            lw_cframe = Frame(lw_topframe, relief=RAISED, bd=2)

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

        return self.__result

def run_test():
    root = Tk()

    # multy variant
    ld_params = {}

    ll_variants = []

                        # tab, text, tooltip, icon, value
    ll_variants.append( ('OS', 'File', 'Process one file', pta_icons.get_icon('gv_options_openfile'), '<file>',) )
    ll_variants.append( ('OS', 'Folder', 'Process folder', pta_icons.get_icon('gv_options_openfolder'), '<folder>',) )

    ll_variants.append( ('Dummies', 'Dummy1', None, pta_icons.get_icon('gv_options_openfolder'), '<dummy1>',) )
    ll_variants.append( ('Dummies', 'Dummy2', None, None, '<dummy2>',) )
    ll_variants.append( ('Dummies', 'Dummy3', None, None, None,) )

    ld_params['variants'] = ll_variants
    ld_params['title'] = 'Select variant'
    ld_params['detail'] = 'Some details here'
    lo_dialog = BaseNBSelector(root,
                               **ld_params
                               )
    print(lo_dialog.show(width=200, height=300, wal=True))

    # single variant
    ld_params = {}

    ll_variants = []

                        #tab, text, tooltip, icon, value
    ll_variants.append( ('OS', 'File', 'Process one file', pta_icons.get_icon('gv_options_openfile'), '<file>',) )

    ld_params['variants'] = ll_variants
    ld_params['title'] = 'Select variant'
    ld_params['detail'] = 'Some details here'
    lo_dialog = BaseNBSelector(root,
                               **ld_params
                              )
    print(lo_dialog.show(width=200, height=300, wal=True))

if __name__ == '__main__':
    run_test()