#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tablelist widget with scrolling and additional
    controls (search, clear, unload, etc.)
"""

# pytkapp.tkw: tablelist widget with scrolling and additional controls
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
import os
import os.path
import codecs
import datetime
import locale
import tempfile
import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    from tkinter import Frame, Scrollbar, StringVar
    from tkinter.constants import N, S, W, E, X, NE, NW, END
    from tkinter.constants import LEFT, RIGHT, VERTICAL, HORIZONTAL
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Frame, Scrollbar, StringVar
    from Tkconstants import N, S, W, E, X, NE, NW, END
    from Tkconstants import LEFT, RIGHT, VERTICAL, HORIZONTAL
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

# pytkapp
from pytkapp.tkw.tablelistwrapper import TableList
from pytkapp.tkw.tkw_searchdialog import SearchDialog
from pytkapp.tkw.tkw_routines import get_estr, toolbar_button_generator, toolbar_separator_generator
import pytkapp.tkw.tkw_icons as tkw_icons
from pytkapp.pta_routines import gv_defenc, tu, convert_fname, novl, xprint
from pytkapp.dia.dia_pumselector import BasePUMSelector
from pytkapp.dia.dia_tlreconfdialog import TLReconfDialog
from pytkapp.dia.dia_tlreconfdialog import TABLELIST_CONFOPTS

###################################
## globals
###################################
XTL_BFG_RESIZE = 'resize'
XTL_BFG_EXPORT = 'export'
gl_bfg = [XTL_BFG_RESIZE, XTL_BFG_EXPORT]

XTL_BF_HIDE = 'HIDE'
XTL_BF_SHOW = 'SHOW'

gl_akw = ['allowsearch',
          'allowresize',
          'allowexport',
          'allowkeepsel',
          'exportdir',
          'hscroll',
          'vscroll',
          'presearchcmd',
          'postsearchcmd',
          'prepopupcmd',
          'postconfcmd']

###################################
## routines
###################################
def datesort( lhs, rhs ):
    """ sort for data in text format """

    lv_out = 0

    lv_lhs = lhs
    lv_rhs = rhs

    # short date
    if len(lhs) == 10:
        lv_source = lhs
        if   lv_source.find('.') != -1 and len(lv_source.split('.')) == 3:
            lv_separator = '.'
        elif lv_source.find('-') != -1 and len(lv_source.split('-')) == 3:
            lv_separator = '-'
        elif lv_source.find('/') != -1 and len(lv_source.split('/')) == 3:
            lv_separator = '/'
        else:
            lv_separator = ''

        if lv_separator != '':
            lv_s = lv_source.split(lv_separator)

            if lv_source.find(lv_separator) == 2:
                lv_lhs = datetime.date(int(lv_s[2]), int(lv_s[1]), int(lv_s[0]))
            else:
                lv_lhs = datetime.date(int(lv_s[0]), int(lv_s[1]), int(lv_s[2]))

    if len(rhs) == 10:
        lv_source = rhs
        if   lv_source.find('.') != -1 and len(lv_source.split('.')) == 3:
            lv_separator = '.'
        elif lv_source.find('-') != -1 and len(lv_source.split('-')) == 3:
            lv_separator = '-'
        elif lv_source.find('/') != -1 and len(lv_source.split('/')) == 3:
            lv_separator = '/'
        else:
            lv_separator = ''

        if lv_separator != '':
            lv_s = lv_source.split(lv_separator)

            if lv_source.find(lv_separator) == 2:
                lv_rhs = datetime.date(int(lv_s[2]), int(lv_s[1]), int(lv_s[0]))
            else:
                lv_rhs = datetime.date(int(lv_s[0]), int(lv_s[1]), int(lv_s[2]))

    lv_out = cmp(lv_lhs, lv_rhs)
    if lv_out not in [0, 1, -1]:
        lv_out = 0

    return lv_out


###################################
## classes
###################################
class XTableList(Frame):
    """ Tablelist with search and additional controls """

    def __init__(self, parent, **kw):
        """ init widget

            kw: contain tablelist-specific keys and some additional:
                allowsearch: True/False - call or not search dialog
                allowresize: True/False - show sizers btns
                allowexport: True/False - add btn to export table to csv
                exportdir: default folder for export
                hscroll: True/False - add or not horizontal scrollbar
                vscroll: True/False - add or not vertical scrollbar
                presearchcmd: if not None than this func will be fired before dialog pop-up
                postsearchcmd: if not None than this func will be fired after dialog closing
                prepopupcmd: None or fnc(widget, event) that fired after B3 before std.popup
                postconfcmd: None or fnc(widget, event) that fired after conf.dialog
        """
        Frame.__init__(self, parent)

        self.__datawidget = None
        self.__lastsearch = None
        self.__presearchcmd = None
        self.__postsearchcmd = None

        self.__udcf = None

        self.__colaliases = []

        # extract additional keywords
        if isinstance(kw, dict):
            ld_kw = kw
        else:
            ld_kw = {}

        self.__xtl_flags = {}
        self.__xtl_flags['allowsearch'] = ld_kw.get('allowsearch', False)
        self.__xtl_flags['allowresize'] = ld_kw.get('allowresize', False)
        self.__xtl_flags['allowexport'] = ld_kw.get('allowexport', False)

        self.__xtl_bf = {}
        self.__xtl_bfp = {}

        self.__exportdir = ld_kw.get('exportdir', os.getcwd())
        self.__presearchcmd = ld_kw.get('presearchcmd', None)
        self.__postsearchcmd = ld_kw.get('postsearchcmd', None)

        self.__prepopupcmd = ld_kw.get('prepopupcmd', None)
        self.__postconfcmd = ld_kw.get('postconfcmd', None)

        self.__kw_hscroll = ld_kw.get('hscroll', False)
        self.__kw_vscroll = ld_kw.get('vscroll', False)

        # clear ld_kw
        for akw in gl_akw:
            ld_kw.pop(akw, None)

        if not ld_kw.has_key('exportselection'):
            ld_kw['exportselection'] = False

        self.__datawidget = TableList(self, **ld_kw)

        ## forward the tablelist methods to myself (Frame)
        methods = TableList.__dict__.keys()
        for m in methods:
            if m not in ('clear',):
                setattr(self, m, getattr(self.__datawidget, m))

        # store default configurable options
        self.__defconfmatrix = {}
        for optkey in TABLELIST_CONFOPTS:
            lv_value = self.__datawidget.cget('-%s' % optkey)
            lv_value = getattr(lv_value, 'string', '%s' % lv_value)
            self.__defconfmatrix['^%s' % optkey] = lv_value

    def get_defconfmatrix(self):
        """get default tlmatrix"""

        return self.__defconfmatrix.copy()

    def get_defconfmatrix_value(self, matrix_key):
        """get value from default tlmatrix"""

        return self.__defconfmatrix.get(matrix_key, '')

    def xcontent(self):
        """ generate widget additional content """

        lb_hscroll = self.__kw_hscroll
        lb_vscroll = self.__kw_vscroll

        lb_allowsearch = self.get_xtl_flag('allowsearch')
        lb_allowresize = self.get_xtl_flag('allowresize')
        lb_allowexport = self.get_xtl_flag('allowexport')

        self.__datawidget.grid(row=0, column=0, sticky=N+E+W+S)
        self.__datawidget.configure( labelcommand = self.on_header_click )

        self.__datawidget.body_bind('<Button-3>', self.call_datawidget_popup, '+')

        lv_mr = 0

        if lb_vscroll:
            vbar = Scrollbar(self, name='vbar', orient=VERTICAL)
            self.__datawidget['yscrollcommand'] = vbar.set
            vbar['command'] = self.__datawidget.yview
            vbar.grid(row=0, column=1, sticky=N+E+W+S)

        if lb_hscroll:
            lv_mr += 1
            hbar = Scrollbar(self, name='hbar', orient=HORIZONTAL)
            self.__datawidget['xscrollcommand'] = hbar.set
            hbar['command'] = self.__datawidget.xview
            hbar.grid(row=lv_mr, column=0, sticky=N+E+W+S)

        Frame.columnconfigure( self, 0, weight=1 )
        Frame.rowconfigure( self, 0, weight=1 )

        if lb_allowsearch:
            self.__lastsearch = StringVar()
            self.__datawidget.body_bind('<Control-KeyPress-f>', self.call_seach_dialog)
            self.__datawidget.body_bind('<F3>', lambda event, m='single': self.call_reseach(m))
            self.__datawidget.body_bind('<Control-F3>', lambda event, m='all': self.call_reseach(m))

        lv_mr += 1
        lw_bottomframe = Frame(self)

        self.__udcf = Frame(lw_bottomframe)
        self.__udcf.pack(side=LEFT, anchor=NW, fill=X)

        lw_cf = Frame(lw_bottomframe)

        lv_r = 0
        lv_c = self.custom_bottom_subframe(lw_cf, lv_r, 0)

        if lb_allowresize or lb_allowexport:

            if lb_allowresize:
                lw_bf = Frame(lw_cf)

                toolbar_button_generator(lw_bf,
                                         _('Resize by data'),
                                         tkw_icons.get_icon('gv_xtablelist_resizebydata'),
                                         self.call_resizebydata,
                                         padx=2, pady=2)

                toolbar_button_generator(lw_bf,
                                         _('Resize by headers'),
                                         tkw_icons.get_icon('gv_xtablelist_resizebyheaders'),
                                         self.call_resizebyheaders,
                                         padx=2, pady=2)

                if lb_allowexport:
                    toolbar_separator_generator(lw_bf, ppadx=3, ppady=2)

                lw_bf.grid(row=lv_r, column=lv_c, sticky=N+E)
                self.__xtl_bf[XTL_BFG_RESIZE] = lw_bf
                self.__xtl_bfp[XTL_BFG_RESIZE] = lv_c
                lv_c += 1

            if lb_allowexport:
                lw_bf = Frame(lw_cf)

                item = toolbar_button_generator(lw_bf,
                                                _('Export data'),
                                                tkw_icons.get_icon('gv_xtablelist_export'),
                                                self.call_export,
                                                padx=2, pady=2)

                lw_bf.grid(row=lv_r, column=lv_c, sticky=N+E)
                self.__xtl_bf[XTL_BFG_EXPORT] = lw_bf
                self.__xtl_bfp[XTL_BFG_EXPORT] = lv_c
                lv_c += 1

        lw_cf.pack(side=RIGHT, anchor=NE)
        lw_bottomframe.grid(row=lv_mr, column=0, columnspan=2, sticky=N+E+W+S, pady=2)

    def custom_bottom_subframe(self, pw_bframe, pv_r, pv_c):
        """ generate custom bottom subframe
            generate content and return next position
        """

        return pv_c

    def get_xtl_flag(self, pv_flag):
        """ get value of xtl flag """

        return self.__xtl_flags.get(pv_flag, None)

    def set_xtl_flag(self, pv_flag, pv_value):
        """ set value of xtl flag """

        self.__xtl_flags[pv_flag] = pv_value

    def get_xtl_bf(self, pv_key):
        """ get item from xtl_bf """

        return self.__xtl_bf.get(pv_key, None)

    def set_xtl_bf(self, pv_key, pv_value):
        """ set item to xtl_bf """

        self.__xtl_bf[pv_key] = pv_value

    def get_xtl_bfp(self, pv_key):
        """ get item from xtl_bfp """

        return self.__xtl_bfp.get(pv_key, None)

    def set_xtl_bfp(self, pv_key, pv_value):
        """ set item to xtl_bfp """

        self.__xtl_bfp[pv_key] = pv_value

    def manage_bottom_frame(self, pv_flag, pv_operation):
        """ hide/show bottom frame btn-groups """

        if pv_flag in gl_bfg:
            if pv_operation in (XTL_BF_HIDE, XTL_BF_SHOW) and self.get_xtl_flag('allow%s' % pv_flag):
                lw_frame = self.__xtl_bf.get(pv_flag, None)
                if lw_frame is not None:
                    if pv_operation == XTL_BF_HIDE:
                        lw_frame.grid_forget()
                    else:
                        lw_frame.grid(row=0, column=self.__xtl_bfp[pv_flag], sticky=N+E)

    def call_datawidget_reconfdialog(self, po_event=None):
        """call datawidget reconfiguration dialog"""

        lo_dialog = TLReconfDialog(self,
                                   title=_('Configuration'),
                                   widget=self)
        lo_dialog.show()

        if self.__postconfcmd:
            self.__postconfcmd(self.__datawidget, po_event)

    def get_tlmatrix(self):
        """get matrix of datawidget"""

        ld_matrix = {}

        lw_tl = self
        lw_table = lw_tl.get_datawidget()

        lt_headers = lw_table.cget('-columntitles')
        ll_aliases = lw_tl.get_aliases()

        if not isinstance(lt_headers, tuple):
            lt_headers = tuple()

        # columns >>>
        for col_indx in range(len(lt_headers)):
            # prepare data
            lv_header = lt_headers[col_indx]

            lv_hide = lw_table.columncget("%s" % col_indx, "-hide")

            ld_coldata = {}
            ld_coldata['hide'] = lv_hide

            ld_matrix[lv_header] = ld_coldata

        # others configurable options >>>
        for optkey in TABLELIST_CONFOPTS:
            lv_value = lw_tl.cget('-%s' % optkey)
            lv_value = getattr(lv_value, 'string', '%s' % lv_value)
            ld_matrix['^%s' % optkey] = lv_value

        return ld_matrix

    def apply_tlmatrix(self, pd_matrix=None):
        """apply matrix"""

        if pd_matrix:
            lw_tl = self
            lw_table = lw_tl.get_datawidget()

            lt_headers = lw_table.cget('-columntitles')
            ll_aliases = lw_tl.get_aliases()

            if not isinstance(lt_headers, tuple):
                lt_headers = tuple()

            # column >>>
            for col_indx in range(len(lt_headers)):
                # prepare data
                lv_header = lt_headers[col_indx]

                ld_matrixdata = pd_matrix.get(lv_header, None)
                if ld_matrixdata:
                    # show/hide columns
                    lv_hide = ld_matrixdata.get('hide', 0)
                    lw_table.columnconfigure("%s" % col_indx, hide=lv_hide)

            # others configurable options
            for mkey, tlkey in [(mkey, mkey[1:],) for mkey in tuple(pd_matrix.keys()) if mkey.startswith('^')]:
                try:
                    lv_value = pd_matrix[mkey]

                    if lv_value == "None":
                        lv_value = None

                    ld_kw = {}
                    ld_kw[tlkey] = lv_value

                    lw_tl.configure(**ld_kw)
                except:
                    print('%s' % get_estr())

    def call_datawidget_popup(self, po_event=None):
        """call pop-up menu from datawidget"""

        if self.__prepopupcmd:
            ll_uservariants = self.__prepopupcmd(self.__datawidget, po_event)
        else:
            ll_uservariants = []

        ll_variants = []
        ll_variants.append(( _('Configuration'), tkw_icons.get_icon('gv_icon_widget_configure'), lambda e=po_event: self.call_datawidget_reconfdialog(e),))

        if ll_uservariants:
            ll_variants += ll_uservariants

        lo_object = BasePUMSelector(self,
                                    po_event,
                                    variants=ll_variants,
                                    tearoff=0)

    def call_pass(self, po_event=None):
        """pass"""

        print('pass')

    def get_aliases(self):
        """ get current aliases """

        return self.__colaliases[:]

    def set_aliases(self, pl_aliases):
        """ set aliases for tablelist """

        self.__colaliases = pl_aliases

    def get_colindex4alias(self, pv_alias):
        """ get index of column by alias """

        for i, data in enumerate(self.__colaliases):
            if data.upper() == pv_alias.upper():
                return i

        raise IndexError

    def get_colindex4title(self, pv_title):
        """ get index of column by title """

        lv_res = self.__datawidget.cget('-columntitles')
        if isinstance(lv_res, tuple) and len(lv_res) > 0:
            for i, data in enumerate(lv_res):
                if data.upper() == pv_title.upper():
                    return i

        raise IndexError

    def get_udcf(self):
        """ return user-defined control frame """

        return self.__udcf

    def call_seach_dialog(self, po_event=None):
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

    def call_reseach(self, pv_mode=None):
        """ process single re-search without pop-up dialog """

        if self.__presearchcmd is not None:
            self.__presearchcmd()

        s = SearchDialog( self,
                          self.__datawidget,
                          lastsearch=self.__lastsearch,
                          research=pv_mode,
                          postsearchcmd=self.__postsearchcmd)

        lv_index = s.get_firstindex()
        if lv_index is not None:
            self.__datawidget.see( lv_index )
            self.__datawidget.update_idletasks()

            return "break"

    def get_datawidget(self):
        """ return datawidget """

        return self.__datawidget

    def call_resizebydata(self, po_event=None):
        """ set width of columns by data """

        for ci in range(self.__datawidget.columncount()):
            self.__datawidget.columnconfigure(ci, width=0)

    def call_resizebyheaders(self, po_event=None):
        """ set width of columns by headers """

        for ci in range(self.__datawidget.columncount()):
            h_len = len(self.__datawidget.columncget(ci,'-title'))+1
            self.__datawidget.columnconfigure(ci, width=h_len)

    def directexport(self, pv_ext):
        """ call export in tempfile or call export routines """

        lv_ext = novl(pv_ext, '').lower()
        lv_exppath = None
        if lv_ext in ('.csv', '.html'):
            try:
                lf_file = tempfile.NamedTemporaryFile(delete=False, suffix=lv_ext)
                lf_file.close()
            except:
                lv_message = get_estr()
                print(lv_message)
            else:
                self.export_(lf_file.name)

                lv_exppath = lf_file.name
        else:
            lv_exppath = self.call_export()

        return lv_exppath

    def export_(self, pv_filename=None):
        """ export routines """

        if novl(pv_filename,'') != '':
            lv_ext = os.path.splitext(pv_filename.lower())[1]
            with codecs.open(pv_filename, 'w+', locale.getpreferredencoding()) as lo_f:
                lv_tlsize = self.__datawidget.size()
                # save header
                lt_headers = self.__datawidget.cget('-columntitles')

                if not isinstance(lt_headers, tuple):
                    lt_headers = tuple()

                if lv_ext == '.csv':
                    lo_f.write(tu(';').join([tu(i) for i in lt_headers])+'\n')
                else:
                    lo_f.write('<!DOCTYPE HTML PUBLIC  "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n')
                    lo_f.write('<HTML>\n')
                    lo_f.write('<HEAD>\n')
                    lo_f.write('<meta http-equiv="Content-Type" content="text/html; charset=%s">\n' % (gv_defenc.replace('_','-')))
                    lo_f.write('<TITLE>%s</TITLE>\n' % (_('Export')))
                    lo_f.write('</HEAD>\n')
                    lo_f.write('<BODY>\n')
                    lo_f.write('<BASEFONT size="2">\n')
                    lo_f.write('<TABLE border="1" cellspacing="0">\n')

                    lo_f.write('<TR>\n')
                    lo_f.write(''.join(['%s%s' % (tu('<TH>'), tu(i)) for i in lt_headers])+'\n')

                # save data
                for ri in range(lv_tlsize):
                    ll_data = list(self.__datawidget.rowcget(ri,"-text"))

                    lv_bg = self.__datawidget.rowcget(ri, '-background')
                    lv_fg = self.__datawidget.rowcget(ri, '-foreground')

                    if getattr(lv_bg, 'string', '') != '':
                        lv_trbg = 'bgcolor="%s"' % lv_bg
                    else:
                        lv_trbg = ''
                    if getattr(lv_fg, 'string', '') != '':
                        lv_trfg = 'fgcolor="%s"' % lv_bg
                    else:
                        lv_trfg = ''

                    if lv_ext == '.csv':
                        lo_f.write(tu(';').join([tu(i) for i in ll_data])+'\n')
                    else:
                        lo_f.write('<TR %s %s>\n' % (lv_trbg, lv_trfg))

                        for i, data in enumerate(ll_data):
                            lv_bg = self.__datawidget.cellcget('%s,%s' % (ri, i), '-background')
                            lv_fg = self.__datawidget.cellcget('%s,%s' % (ri, i), '-foreground')

                            if getattr(lv_bg, 'string', '') != '':
                                lv_tdbg = 'bgcolor="%s"' % lv_bg
                            else:
                                lv_tdbg = ''
                            if getattr(lv_fg, 'string', '') != '':
                                lv_tdfg  = '<span style="color:%s">' % (lv_fg)
                                lv_tdfg2 = '</span>'
                            else:
                                lv_tdfg  = ''
                                lv_tdfg2 = ''

                            if novl(tu(data), '').strip() == '':
                                lv_data = '&nbsp;'
                            else:
                                lv_data = data

                            lo_f.write('<TD %s>%s%s%s' % (lv_tdbg, lv_tdfg, lv_data, lv_tdfg2))

                            if i == len(ll_data) - 1:
                                lo_f.write('\n')

                if lv_ext == '.html':
                    lo_f.write('</TABLE>\n')
                    lo_f.write('</BODY>\n')
                    lo_f.write('</HTML>\n')

    def call_export(self, po_event=None):
        """ export table to csv-file """

        lv_exppath = None
        lv_defexportpath = self.__exportdir
        if not os.path.isdir(lv_defexportpath):
            lv_defexportpath = os.getcwd()
            xprint('Warning! Default folder for export doesnt exists: %s'%(self.__exportdir))

        lv_exportpath = filedialog.asksaveasfilename(title=_('Export data'),
                                                     filetypes = {"csv-file {.csv}":0,
                                                                  "html-file {.html}":1},
                                                     initialdir=lv_defexportpath,
                                                     defaultextension='csv',
                                                     parent=self.__datawidget.winfo_toplevel()
                                                     )
        lv_exportpath = convert_fname( lv_exportpath )

        if novl(lv_exportpath,'') != '':
            lv_exportpath = os.path.realpath(lv_exportpath).lower()

            lv_ext = os.path.splitext(lv_exportpath.lower())[1]

            if lv_ext not in ('.csv', '.html'):
                lv_exportpath += '.csv'
                lv_ext = '.csv'

            lv_folder = os.path.split(lv_exportpath)[0]
            if os.path.exists(lv_folder):

                self.export_(lv_exportpath)
                lv_exppath = lv_exportpath

                messagebox.showinfo(_('Info'),
                                    _('Export completed !'),
                                    detail=lv_exportpath,
                                    parent=self.__datawidget.winfo_toplevel())

        return lv_exppath

    def on_header_click( self, pv_tlpath, pv_column ):
        """ process sorting for column """

        lv_order = "-increasing"
        if self.__datawidget.sortcolumn() == int(pv_column) and self.__datawidget.sortorder() == "increasing":
            lv_order = "-decreasing"

        self.__datawidget.sortbycolumn(pv_column, lv_order)

    def clear_(self, po_event=None):
        """ clear internal structires """

        self.__colaliases = []
        if self.__lastsearch is not None:
            self.__lastsearch.set('')

    def clear_data(self, po_event=None):
        """ clear all stored data """

        lv_table = self.__datawidget

        lv_table.grid_remove()
        try:
            lv_table.delete(0, "end")
        finally:
            lv_table.grid()

    def insert_data(self, lv_pos=END, lt_data=()):
        """simple insert data"""

        self.__datawidget.insert(lv_pos, lt_data)

    def clear(self, po_event=None):
        """ clear all content of widget """

        lv_table = self.__datawidget

        lv_table.grid_remove()
        try:
            lv_table = self.__datawidget
            lt_ct = lv_table.cget('-columntitles')
            if isinstance(lt_ct, tuple) and len(lt_ct) > 0:
                lv_table.deletecolumns(0, len(lt_ct)-1)

            lv_table.delete(0, "end")
            lv_table.resetsortinfo()
        finally:
            lv_table.grid()

        self.clear_()
