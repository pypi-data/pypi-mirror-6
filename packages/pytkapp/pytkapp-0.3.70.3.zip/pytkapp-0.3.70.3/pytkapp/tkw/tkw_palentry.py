#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" entry with color fill and color selector """

# pytkapp.tkw: entry with color fill and color selector
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
    from tkinter import Tk, Entry
    import tkinter.tkcolorchooser as tkcolorchooser
    from tkinter.constants import CENTER
else:
    from Tkinter import Tk, Entry
    import tkColorChooser as tkcolorchooser
    from Tkconstants import CENTER

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
from pytkapp.tkw.tkw_routines import make_widget_ro, novl
           
###################################
## globals
###################################
gt_allowed_options = ('state', 'width',)
           
###################################
## classes
###################################
class PalEntry(Entry):
    """paletted entry"""

    def __init__(self, master, **kw):
        """ init widget """

        self._currcolor = None
        self._origcolor = None
        self._master    = master

        ld_kw = kw.copy()
        
        self._textvariable = kw.get('textvariable', None)
        
        if self._textvariable:
            lv_color = novl(self._textvariable.get(), '')
        else:
            lv_color = ''
                            
        lv_color = novl(kw.get('color', lv_color), '')
        if lv_color == '':
            lv_color = 'black'

        lv_ocolor = novl(kw.get('ocolor', lv_color), '')
        if lv_ocolor == '':
            lv_ocolor = 'black'
            
        self._origcolor = lv_ocolor
        
        for kwkey in kw:
            if kwkey not in gt_allowed_options:
                ld_kw.pop(kwkey)
                                
        ld_kw['cursor'] = "arrow"
        ld_kw['highlightthickness'] = 0
        ld_kw['insertwidth'] = 0
        ld_kw['insertofftime'] = 9999
        ld_kw['insertontime'] = 1
        ld_kw['exportselection'] = 0
        ld_kw['justify'] = CENTER
        
        ld_kw.setdefault('width', 10)
       
        Entry.__init__(self, master, **ld_kw)
        
        make_widget_ro(self)
        self.bind('<Double-Button-1>', self._call_select_color)
        self.bind('<Button-3>', self._call_revert_color)
        
        self.set(lv_color)
        
    def _get_master(self):
        """get original master"""
        
        return self._master
    
    def _call_revert_color(self, po_event=None):
        """revert color to original state"""
        
        lv_value = self._origcolor
        self.set(lv_value)  
        
    def _call_select_color(self, po_event=None):
        """select color"""
        
        lv_rgb, lv_hex = tkcolorchooser.askcolor(color=self._currcolor, 
                                                 title=_('Select color'),
                                                 parent=self._master)
        if lv_hex:
            self.set(lv_hex)        
        
    def set(self, pv_color):
        """set color"""
        
        lv_color = novl(pv_color, '')
        if lv_color == '':
            lv_color = "black"
        
        ld_kw = {}
        ld_kw['bg'] = lv_color
        ld_kw['insertbackground'] = lv_color
        
        self._configure__(**ld_kw)
        self._currcolor = lv_color
        
        if self._textvariable:
            self._textvariable.set(lv_color)
    
    def get(self):
        """get color"""
        
        return novl(self._currcolor, "black")
    
    def _configure__(self, **kw):
        """call original configure method"""
        
        Entry.configure(self, **kw)

    def configure( self, **kw ):
        """ configure widget """

        ld_kw = kw.copy()

        for kwkey in kw:
            if kwkey not in gt_allowed_options:
                ld_kw.pop(kwkey)
                
        if kw.has_key('textvariable'):
            self._textvariable = kw.get('textvariable', None)
                        
        if self._textvariable:
            self._textvariable.set(self._currcolor)        
        
        self._configure__(**ld_kw)

def run_demo():
    """demo"""
    
    root = Tk()
    root.title('demo')    
    
    lw_pe = PalEntry(root)
    lw_pe.pack()
    
    print(lw_pe.get())
    
    root.mainloop()
    
if __name__ == '__main__':
    
    run_demo()