#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - pop-up selector based on menu """

# pytkapp: common dialogs - pop-up selector based on menu
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
    from tkinter import Tk, PhotoImage, Frame, Menu
    from tkinter.constants import LEFT
else:
    from Tkinter import Tk, PhotoImage, Frame, Menu
    from Tkconstants import LEFT

# pytkapp
import pytkapp.pta_icons as pta_icons

###################################
## globals
###################################

###################################
## routines
###################################
def pass_print(pv_arg):
    """call print from anywere"""
    print('called from %s' % pv_arg)

###################################
## classes
###################################
class BasePUMSelector(Menu):
    """ sample of selector dialog from menu """

    def __init__(self, pw_parent, po_event, **kw):
        """ init routines """

        # title, icon, command
        ll_variants = kw.pop('variants', [])
        self.__images = []

        Menu.__init__(self, pw_parent, **kw)

        lw_menu = self

        lw_mainmenu = self
        ld_menugroups = {}

        if ll_variants:
            for varindx, vardata in enumerate(ll_variants):
                if vardata[0] == '<separator>':
                    lw_menu.add_separator()
                elif vardata[0] == '<groupheader>':
                    lv_groupname = vardata[1]
                    ld_menugroups[lv_groupname] = lw_menu
                    lw_nmenu = Menu(self, tearoff=0)
                    lw_menu.add_cascade(label=_(lv_groupname), menu=lw_nmenu)
                    lw_menu = lw_nmenu
                elif vardata[0] == '<grouptail>':
                    lv_groupname = vardata[1]
                    lw_menu = ld_menugroups.get(lv_groupname, lw_mainmenu)
                # obsoletted mode - dont use !
                elif vardata[0] == '<userdefined>':
                    lv_groupname = _('User-defined')
                    ld_menugroups[lv_groupname] = lw_menu
                    lw_nmenu = Menu(self, tearoff=0)
                    lw_menu.add_cascade(label=_(lv_groupname), menu=lw_nmenu)
                    lw_menu = lw_nmenu
                    #lw_menu.add_separator()
                    #lw_menu = Menu(self, tearoff=0)
                    #self.add_cascade(label=_('User-defined'), menu=lw_menu)
                else:
                    menutitle, menuicon, menucommand = vardata

                    if menuicon:
                        lo_image = PhotoImage(data=menuicon)
                        self.__images.append(lo_image)
                    else:
                        lo_image = None

                    lw_menu.add_command(label=menutitle, command=menucommand, compound=LEFT, image=lo_image)

            #self.post(po_event.x_root, po_event.y_root)
            self.tk_popup(po_event.x_root, po_event.y_root)
        else:
            print('variants list is empty !')

def run_test():
    """run test"""

    root = Tk()


    frame = Frame(root, width=400, height=300)
    frame.pack()

    ll_variants = []
                        # text, icon, command
    ll_variants.append( ('File',   pta_icons.get_icon('gv_options_openfile'), lambda a='var:file': pass_print(a),) )
    ll_variants.append( ('Folder', pta_icons.get_icon('gv_options_openfolder'), lambda a='var:folder': pass_print(a),) )

    ll_variants.append( ('<separator>', ))

    ll_variants.append( ('Dummy1', pta_icons.get_icon('gv_options_openfolder'), lambda a='var:d1': pass_print(a),) )

    ll_variants.append( ('<groupheader>', 'Dummy1-group',))

    ll_variants.append( ('Dummy1.1', None, lambda a='var:d1.1': pass_print(a),) )
    ll_variants.append( ('Dummy1.2', None, lambda a='var:d1.2': pass_print(a),) )

    ll_variants.append( ('<grouptail>', 'Dummy1-group',))

    ll_variants.append( ('<separator>', ))

    ll_variants.append( ('Dummy2', None, lambda a='var:d2': pass_print(a),) )

    ll_variants.append( ('<userdefined>', ))

    ll_variants.append( ('Dummy2.1', None, lambda a='var:d2.1': pass_print(a),) )
    ll_variants.append( ('Dummy2.2', None, lambda a='var:d2.2': pass_print(a),) )

    frame.bind("<Button-3>", lambda e, f=frame: BasePUMSelector(f, e, variants=ll_variants, tearoff=0))

    root.mainloop()

if __name__ == '__main__':
    run_test()