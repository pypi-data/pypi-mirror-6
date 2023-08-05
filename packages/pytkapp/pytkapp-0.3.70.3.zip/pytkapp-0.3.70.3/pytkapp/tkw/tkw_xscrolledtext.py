#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" text widget with scrolling and additional
    controls (search, clear, unload, etc.)
"""

# pytkapp.tkw: text widget with scrolling and additional controls
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
import tempfile
import locale
import gettext
import codecs
import os
import subprocess
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    from tkinter import Text, Frame, Scrollbar, StringVar, Entry, TclError
    from tkinter.constants import N, S, W, E, SEL, INSERT
    from tkinter.constants import TOP, LEFT, X, END, YES, BOTH, HORIZONTAL, VERTICAL, CURRENT
    from tkinter.constants import NONE, CHAR, NORMAL, DISABLED
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Text, Frame, Scrollbar, StringVar, Entry, TclError
    from Tkconstants import N, S, W, E, SEL, INSERT
    from Tkconstants import TOP, LEFT, X, END, YES, BOTH, HORIZONTAL, VERTICAL, CURRENT
    from Tkconstants import NONE, CHAR, NORMAL, DISABLED
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.tkw.tkw_searchdialog import SearchDialog
from pytkapp.tkw.tkw_routines import make_widget_ro, READONLY, get_estr
from pytkapp.dia.dia_pumselector import BasePUMSelector
from pytkapp.dia.dia_textreconfdialog import TextReconfDialog
from pytkapp.dia.dia_textreconfdialog import XSCROLLEDTEXT_CONFOPTS, XSCROLLEDTEXT_TAGS
import pytkapp.tkw.tkw_icons as tkw_icons
from pytkapp.pta_routines import convert_fname, novl, get_currentfolder, xprint, gv_defenc

###################################
## constants
###################################
STRIP_MODE_ALL = 'all'
STRIP_MODE_LAST = 'last'

XTEXT_COLOR_INFO    = '#d5ffd5'
XTEXT_COLOR_WARNING = '#ffffbb'
XTEXT_COLOR_ERROR   = '#ffcccc'
XTEXT_COLOR_ASK     = '#ccccff'
XTEXT_COLOR_MARK    = '#ffff00'

###################################
## classes
###################################
class XScrolledText(Frame):
    """ scrolledtext with additional functional
        contain widgets for clearing, unloading to file and searching
        kw:
           unloaddir/exportdir - folder for export text
           importdir - folder for import text
           defext - default extension for imported/exported files
           defwidth - default width
           defheight - default height
           presearchcmd - routine that fired before search dialog pop-up
           postsearchcmd - routine that fired after search dialog closed
           search - True/False - allow search
           clear - True/False - allow clear text
           unload/export_ - True/False - allow unload text
           import_ - True/False - allow import text
           print_ - True/False - allow print text
           wrap - if NONE then provide horizontal scrollbar for widget
           wstate - NORMAL/DISABLED/READONLY (default)
           transpalette - transparent palette (use default bg for all marks) - True (by default)/False
           prepopupcmd: None or fnc(widget, event) that fired after B3 before std.popup
           postconfcmd: None or fnc(widget, event) that fired after conf.dialog
    """

    def __init__(self, master, **kw):
        """ init widget """

        Frame.__init__(self, master)

        # some attrs
        self.__exportdir = kw.get('exportdir', kw.get('unloaddir', get_currentfolder()))
        self.__importdir = kw.get('importdir', get_currentfolder())
        self.__defext    = kw.get('defext', 'txt')

        self.__prepopupcmd = kw.get('prepopupcmd', None)
        self.__postconfcmd = kw.get('postconfcmd', None)

        # widgets
        lw_mainframe = Frame(self)
        ld_kw = {}
        for kw_key in kw:
            if kw_key == 'defwidth':
                ld_kw['width'] = kw[kw_key]
            elif kw_key == 'defheight':
                ld_kw['height'] = kw[kw_key]
            elif kw_key in ('wstate', 'presearchcmd', 'postsearchcmd',
                            'search', 'clear', 'import_', 'export_', 'unload', 'print_',
                            'unloaddir', 'exportdir', 'importdir', 'defext',
                            'prepopupcmd', 'transpalette', ):
                pass
            else:
                ld_kw[kw_key] = kw[kw_key]

        self.__datawidget = Text(lw_mainframe,
                                 **ld_kw)
        self.__datawidget.grid(column=0, row=0, sticky=N+E+W+S)
        self.__datawidget.bind('<Button-3>', self.call_datawidget_popup, '+')

        self.__datawidget.bind('<Control-a>', self._call_selectall_text)
        self.__datawidget.bind('<Control-A>', self._call_selectall_text)

        lw_vsb = Scrollbar(lw_mainframe)
        lw_vsb.config(orient=VERTICAL, command=self.__datawidget.yview)
        lw_vsb.grid(column=1, row=0, sticky=N+S)
        self.__datawidget.config(yscrollcommand=lw_vsb.set)

        if ld_kw.get('wrap', CHAR) == NONE:
            lw_hsb = Scrollbar(lw_mainframe)
            lw_hsb.config(orient=HORIZONTAL, command=self.__datawidget.xview)
            lw_hsb.grid(column=0, row=1, sticky=E+N+W)
            self.__datawidget.config(xscrollcommand=lw_hsb.set)

        # simple palette and default background color
        self.__palette = {}
        self.__palette['info']    = XTEXT_COLOR_INFO
        self.__palette['warning'] = XTEXT_COLOR_WARNING
        self.__palette['error']   = XTEXT_COLOR_ERROR
        self.__palette['ask']     = XTEXT_COLOR_ASK

        self.__defpalette = {}
        self.__defpalette['bg']   = self.__datawidget.cget('bg')
        self.__defpalette['fg']   = self.__datawidget.cget('fg')
        lw_temp = Entry(self)
        self.__defpalette['dbg']  = lw_temp.cget('disabledbackground')
        self.__defpalette['dfg']  = lw_temp.cget('disabledforeground')
        lw_temp.destroy()
        self.__defpalette['mark'] = XTEXT_COLOR_MARK

        # re-paint for widget state
        self.set_wstate(kw.get('wstate', READONLY))

        lw_mainframe.columnconfigure(0, weight=1)
        lw_mainframe.rowconfigure(0, weight=1)

        lw_mainframe.pack(side=TOP, expand=YES, fill=BOTH, padx=1, pady=1)

        # store some user-defined points
        self.__marks = {}
        # store tags that was associated with text
        self.__tags = []



        self.__docmds = {}
        self.__docmds['search'] = self.call_seach_dialog
        self.__docmds['clear']  = self.call_clear_data
        self.__docmds['import'] = self.call_import_data
        self.__docmds['export'] = self.call_export_data
        self.__docmds['print']  = self.call_print_data

        # store options for routines
        self.__dosearch = kw.get('search', False)
        self.__doclear  = kw.get('clear', False)
        self.__doimport = kw.get('import_', False)
        self.__doexport = kw.get('unload', False) or kw.get('export_', False)
        self.__doprint  = kw.get('print_', False)

        # associate search dialog
        self.__lastsearch = None
        self.__presearchcmd = None
        self.__postsearchcmd = None
        if kw.get('search', False):
            self.__lastsearch = StringVar()
            self.__presearchcmd = kw.get('presearchcmd', None)
            self.__postsearchcmd = kw.get('postsearchcmd', None)
            self.__datawidget.bind('<Control-KeyPress-f>', self.call_seach_dialog)

        self.__udcf = Frame(self)
        self.__udcf.pack(side=LEFT, fill=X, padx=1, pady=1)

        self.__wcontrols = {}

        # hide palette by default
        if kw.get('transpalette', True):
            self.hide_palette()

        # store default configurable options
        self.__defconfmatrix = {}
        for optkey in XSCROLLEDTEXT_CONFOPTS:
            lv_value = self.__datawidget.cget('%s' % optkey)
            lv_value = getattr(lv_value, 'string', '%s' % lv_value)
            self.__defconfmatrix['^%s' % optkey] = lv_value
        for optkey in XSCROLLEDTEXT_TAGS:
            lv_value = self.get_palette_color(optkey)
            lv_value = getattr(lv_value, 'string', '%s' % lv_value)
            self.__defconfmatrix['@%s' % optkey] = lv_value

    def get_defconfmatrix(self):
        """get default conf.matrix"""

        return self.__defconfmatrix.copy()

    def get_defconfmatrix_value(self, matrix_key):
        """get value from default tlmatrix"""

        return self.__defconfmatrix.get(matrix_key, '')

    def hide_palette(self):
        """set palette colors to def bg and change colors for tags"""

        # set new colors for palette
        lv_bg = self.__datawidget.cget('bg')
        self.__defpalette['bg']   = lv_bg
        self.__defpalette['mark'] = lv_bg

        for palkey in list(self.__palette.keys()):
            self.__palette[palkey] = lv_bg

        # re-paint text
        self.apply_palette()

    def reset_palette(self):
        """set default colors for palette and tags"""

        lv_bg = self.__datawidget.cget('bg')
        lv_mark = XTEXT_COLOR_MARK

        # set new colors for palette
        self.__defpalette['bg']   = lv_bg
        self.__defpalette['mark'] = lv_mark

        for palkey in [pkey for pkey in self.__palette.keys() if pkey not in ('info', 'warning', 'error', 'ask',)]:
            self.__palette[palkey] = lv_mark

        self.__palette['info']    = XTEXT_COLOR_INFO
        self.__palette['warning'] = XTEXT_COLOR_WARNING
        self.__palette['error']   = XTEXT_COLOR_ERROR
        self.__palette['ask']     = XTEXT_COLOR_ASK

        # re-paint text
        self.apply_palette()

    def import_palette(self, pd_key='tags', pd_palette=None):
        """set palette from dict"""

        if pd_palette:
            if   pd_key == 'tags':
                self.__palette.update(pd_palette)
            elif pd_key == 'default':
                self.__defpalette.update(pd_palette)

    def export_palette(self, pd_key='tags'):
        """get palette from dict"""

        if   pd_key == 'tags':
            return self.__palette.copy()
        elif pd_key == 'default':
            return self.__defpalette.copy()
        else:
            return None

    def apply_palette(self):
        """apply current state of palette to widget"""

        for tag in self.__tags:
            if tag.startswith('!'):
                lv_tagname = tag.split('-')[0][1:]
            else:
                lv_tagname = tag

            lv_tagbg = self.__palette.get(lv_tagname, None)
            if not lv_tagbg:
                lv_tagbg = self.__defpalette.get('mark', None)

            if lv_tagbg:
                self.__datawidget.tag_configure(tag, background=lv_tagbg)
            else:
                self.__datawidget.tag_configure(tag, background=self.__defpalette.get('bg', None))

    def get_palette(self):
        """return palette keys"""

        return list(self.__palette.keys())

    def in_palette(self, pv_key):
        """check key in palette"""

        return self.__palette.has_key(pv_key)

    def set_palette_color(self, pv_key, pv_value=None):
        """set color"""

        self.__palette[pv_key] = pv_value

    def get_palette_color(self, pv_key, pv_dvalue=None):
        """get color"""

        return self.__palette.get(pv_key, pv_dvalue)

    def set_defpalette_color(self, pv_key, pv_value=None):
        """set defcolor"""

        self.__defpalette[pv_key] = pv_value

    def get_defpalette_color(self, pv_key, pv_dvalue=None):
        """get default color"""

        return self.__defpalette.get(pv_key, pv_dvalue)

    def reset_docmd(self, cmdname):
        """set default command for cmdname"""

        if cmdname == 'search':
            self.__docmds[cmdname] = self.call_seach_dialog
        elif cmdname == 'clear':
            self.__docmds[cmdname]  = self.call_clear_data
        elif cmdname == 'import':
            self.__docmds[cmdname] = self.call_import_data
        elif cmdname == 'export':
            self.__docmds[cmdname] = self.call_export_data
        elif cmdname == 'print':
            self.__docmds[cmdname]  = self.call_print_data

    def set_docmd(self, cmdname, cmdbody):
        """set custom cmd for cmdname"""

        if cmdname in self.__docmds:
            self.__docmds[cmdname]  = cmdbody

    def call_datawidget_popup(self, po_event=None):
        """call pop-up menu from datawidget"""

        if self.__prepopupcmd:
            ll_uservariants = self.__prepopupcmd(self.__datawidget, po_event)
        else:
            ll_uservariants = []

        ll_variants = []

        ll_variants.append(( _('Select all'), None, self._call_selectall_text, ))
        if self.__dosearch or self.__doprint or self.__doclear:
            ll_variants.append(('<separator>',))

        if self.__dosearch:
            ll_variants.append(( _('Search'), tkw_icons.get_icon('gv_alistbox_search'), self.__docmds['search'], ))

        if self.__doprint:
            ll_variants.append(( _('Print'), tkw_icons.get_icon('gv_xscrolledtext_print'), self.__docmds['print'], ))

        if self.__doclear:
            ll_variants.append(( _('Clear'), tkw_icons.get_icon('gv_xscrolledtext_clear'), self.__docmds['clear'], ))

        if len(ll_variants) > 1 and (self.__doimport or self.__doexport):
            ll_variants.append(('<separator>',))

        if self.__doimport:
            ll_variants.append(( _('Import'), tkw_icons.get_icon('gv_xscrolledtext_import'), self.__docmds['import'], ))

        if self.__doexport:
            ll_variants.append(( _('Export'), tkw_icons.get_icon('gv_xscrolledtext_export'), self.__docmds['export'], ))

        # configuration
        if len(ll_variants) > 1:
            ll_variants.append(('<separator>',))
            ll_variants.append(( _('Configuration'), tkw_icons.get_icon('gv_icon_widget_configure'), lambda e=po_event: self.call_datawidget_reconfdialog(e),))

        if ll_uservariants:
            ll_variants += ll_uservariants

        if ll_variants:
            lo_object = BasePUMSelector(self,
                                        po_event,
                                        variants=ll_variants,
                                        tearoff=0)

    def call_datawidget_reconfdialog(self, po_event=None):
        """call datawidget reconfiguration dialog"""

        lo_dialog = TextReconfDialog(self,
                                     title=_('Configuration'),
                                     widget=self)
        lo_dialog.show()

        if self.__postconfcmd:
            self.__postconfcmd(self.__datawidget, po_event)

    def get_wcontrols(self, wkey):
        """ return some controls """

        return self.__wcontrols.get(wkey, None)

    def set_wcontrols(self, wkey, wobj):
        """ set some controls """

        self.__wcontrols[wkey] = wobj

    def get_udcf(self):
        """ return user-defined control frame """

        return self.__udcf

    def call_seach_dialog(self, event=None):
        """ call search dialog for widget """

        if self.__presearchcmd is not None:
            self.__presearchcmd()

        s = SearchDialog( self,
                          self.__datawidget,
                          lastsearch=self.__lastsearch,
                          postsearchcmd=self.__postsearchcmd)

        lv_index = s.get_firstindex()
        if lv_index is not None:
            self.__datawidget.see( lv_index )
            self.__datawidget.update_idletasks()

            return "break"

    def _call_selectall_text(self, po_event=None):
        """selectall text"""

        self.__datawidget.focus()
        self.__datawidget.tag_add(SEL, "1.0", END)
        self.__datawidget.mark_set(INSERT, "1.0")
        self.__datawidget.see(INSERT)
        return 'break'

    def call_print_data(self, event=None):
        """ print some data """

        if messagebox.askokcancel(_('Confirm'), _('Print data ?'), parent=self):
            try:
                lf_temp = tempfile.NamedTemporaryFile(suffix='.tmp', delete=False)
                lv_txtdata = ''
                try:
                    lv_txtdata = self.__datawidget.get("sel.first","sel.last")

                except TclError:
                    lv_txtdata = self.get_data()
                finally:
                    lf_temp.write(lv_txtdata.encode(gv_defenc))
                    lf_temp.close()

                # prepare temp file
                if sys.platform == 'win32':
                    subprocess.call(('notepad', '/p', '%s'%lf_temp.name))
                else:
                    subprocess.call(('lpr', '-p', lf_temp.name))
            except:
                lv_message = get_estr()
                print('Print error: %s' % lv_message)
            else:
                os.remove(lf_temp.name)

    def call_import_data(self, event=None):
        """ import data """

        lv_path = filedialog.askopenfilename(title=_('Import data'),
                                             filetypes = {"%s {.%s}" % (_('Data'), self.__defext):0,
                                                          "%s {.*}"  % (_('All')):1},
                                             initialdir=self.__importdir,
                                             parent=self
                                            )
        lv_path = convert_fname( lv_path )

        if novl(lv_path, '') != '':
            lv_path = os.path.realpath(lv_path)

            with codecs.open(lv_path, 'rb', encoding=locale.getpreferredencoding(), errors='replace') as lf_in:
                self.clear_data()
                lv_data = lf_in.read().replace('\r\n', '\n')
                self.insert_data(lv_data, True, '1.0')

                xprint(_('Import completed !'))
        else:
            lv_path = None

        return lv_path

    def call_export_data(self, event=None):
        """ unload data """

        lv_unloadpath = filedialog.asksaveasfilename(title=_('Export data'),
                                                     filetypes = {"%s {.%s}"%(_('Data'), self.__defext):0},
                                                     initialdir=self.__exportdir,
                                                     parent=self,
                                                     defaultextension=self.__defext
                                                     )
        lv_unloadpath = convert_fname( lv_unloadpath )

        if novl(lv_unloadpath, '') != '':
            lv_unloadpath = os.path.realpath(lv_unloadpath.lower())

            if self.__defext.isalnum():
                if os.path.splitext(lv_unloadpath)[-1] != '.%s'%self.__defext:
                    lv_unloadpath += '.%s'%self.__defext

            if os.path.exists(os.path.split(lv_unloadpath)[0]):
                with codecs.open(lv_unloadpath, 'w', encoding=locale.getpreferredencoding()) as lf_out:
                    lf_out.write(self.get_data())

                messagebox.showinfo(_('Info'),
                                    _('Export completed !'),
                                    detail=lv_unloadpath,
                                    parent=self.__datawidget.winfo_toplevel())
        else:
            lv_unloadpath = None

        return lv_unloadpath

    def get_data(self, startpos='1.0', endpos=END, strip_=None):
        """ return content of data widget """

        lv_data = self.__datawidget.get(startpos, endpos)

        if strip_ == STRIP_MODE_ALL:
            return lv_data.strip()
        elif strip_ == STRIP_MODE_LAST:
            try:
                return lv_data[:-1]
            except LookupError:
                return lv_data
        else:
            return lv_data

    def call_clear_data(self, event=None):
        """ clear log text """

        if messagebox.askokcancel(_('Confirm'), _('Clear data ?'), parent=self):
            self.clear_data()

    def clear_data(self):
        """ clear text """

        self.__datawidget.delete('1.0', END)

    def delete_data(self):
        """ clear text """

        self.__datawidget.delete('1.0', END)

    def storedatawidgetendmark(self, pv_key='end'):
        """store value of end mark"""

        self.__marks[pv_key] = self.__datawidget.index(END)

    def storedatawidgetendl1mark(self, pv_key='end-1l'):
        """store value of end mark"""

        self.__marks[pv_key] = self.__datawidget.index("end - 1 lines")

    def storedatawidgetinsertmark(self, pv_key='insert'):
        """store value of insert mark"""

        self.__marks[pv_key] = self.__datawidget.index(INSERT)

    def storedatawidgetcurrentmark(self, pv_key='current'):
        """store value of current end mark"""

        self.__marks[pv_key] = self.__datawidget.index(CURRENT)

    def tag_data(self, pv_tagname, pv_key1=None, pv_key2=None):
        """create tag on region between pv_key1, pv_key2 (or END)"""

        lv_pos1 = self.__marks.get(pv_key1, self.__datawidget.index(CURRENT))
        lv_pos2 = self.__marks.get(pv_key2, self.__datawidget.index("end - 1 lines"))

        if pv_tagname in ('!info', '!warning', '!error', '!ask',):
            lv_tagname = '%s-%s-%s' % (pv_tagname, lv_pos1, lv_pos2)
            lv_tagbg = self.get_palette_color(pv_tagname[1:], self.get_defpalette_color('bg'))
        elif pv_tagname.startswith('#'):
            lv_tagname = '%s-%s-%s' % (pv_tagname, lv_pos1, lv_pos2)
            lv_tagbg = self.get_defpalette_color('mark')
            self.set_palette_color(lv_tagname, lv_tagbg)
        else:
            lv_tagname = pv_tagname
            lv_tagbg = self.get_defpalette_color('mark')
            self.set_palette_color(lv_tagname, lv_tagbg)

        # store tag
        self.__tags.append(lv_tagname)

        # mark tag and set color
        self.__datawidget.tag_add(lv_tagname, lv_pos1, lv_pos2)
        if lv_tagbg:
            self.__datawidget.tag_configure(lv_tagname, background=lv_tagbg)

    def insert_data(self, text, see_=False, position=END):
        """ insert text to data widget """

        self.__datawidget.insert(position, text)
        if see_:
            try:
                self.__datawidget.get("sel.first","sel.last")
            except:
                lb_sel = False
            else:
                lb_sel = True

            if not lb_sel:
                self.see_position(position)

    def get_datawidget(self):
        """ return datawidget """

        return self.__datawidget

    def set_wstate(self, pv_state=NORMAL):
        """ change state of widget: NORMAL/DISABLED/RO """

        lv_bg = self.get_defpalette_color('bg')
        lv_fg = self.get_defpalette_color('fg')
        lv_dbg = self.get_defpalette_color('dbg')
        lv_dfg = self.get_defpalette_color('dfg')

        if pv_state == NORMAL:
            self.__datawidget.configure(state=NORMAL, bg=lv_bg, fg=lv_fg, insertwidth=2, takefocus=1, insertofftime=300)
            self.__datawidget.unbind('<Any-KeyPress>')
        elif pv_state == DISABLED:
            self.__datawidget.configure(state=NORMAL, bg=lv_dbg, fg=lv_dfg, insertwidth=0, takefocus=0, insertofftime=0)
            make_widget_ro(self.__datawidget)
        elif pv_state == READONLY:
            self.__datawidget.configure(state=NORMAL, bg=lv_bg, fg=lv_fg, insertwidth=0, takefocus=1, insertofftime=0)
            make_widget_ro(self.__datawidget)

    def see_position(self, position=END):
        """ see specified position """

        try:
            self.__datawidget.see(position)
        except:
            pass
