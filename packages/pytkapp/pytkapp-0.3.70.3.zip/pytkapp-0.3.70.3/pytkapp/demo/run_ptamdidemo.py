#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for MDI app """

# pytkapp: demo for MDI app
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

import sys
import pytkapp.pta_appinfo as pytkapp_info
sys.modules['pytkapp_info'] = pytkapp_info

pytkapp_info.__appname__ = 'PyTkApp MDI Demo'
pytkapp_info.__appdesc__ = 'PyTkApp MDI Demo'

############################################################
## this object will catch sys.stdout, sys.stderr
############################################################
from pytkapp.pta_logger import get_greedlogger
go_greedlogger = get_greedlogger()

###################################
## import
###################################
import time
import threading
import itertools
import os
import codecs

import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    from tkinter import Entry
    from tkinter import Label, LabelFrame, Frame, Button
    from tkinter.constants import YES, BOTH, X, N, S, W, E, LEFT, NONE, DISABLED, NORMAL, RAISED, TOP, NW
    import tkinter.filedialog as filedialog
else:
    from Tkinter import Entry
    from Tkinter import Label, LabelFrame, Frame, Button
    from Tkconstants import YES, BOTH, X, N, S, W, E, LEFT, NONE, DISABLED, NORMAL, RAISED, TOP, NW
    import tkFileDialog as filedialog

import pytkapp.pta_icons as pta_icons
from pytkapp.tkw.tkw_routines import make_widget_resizeable, READONLY
from pytkapp.tkw.tkw_routines import toolbar_button_generator, toolbar_separator_generator, toolbar_lbutton_generator
from pytkapp.tkw.tkw_routines import toplevel_header, toplevel_footer
from pytkapp.tkw.tkw_xscrolledtext import XScrolledText
from pytkapp.tkw.tkw_extablelist import EXTableList

from pytkapp.dia.dia_selector import BaseSelector

from pytkapp.pta_child import BaseChild
from pytkapp.pta_app import BaseApp, APP_UI_MODE_MDI
from pytkapp.pta_routines import novl, get_estr, print_envdata
from pytkapp.pta_routines import convert_fname, get_currentfolder, xprint, gv_defenc
from pytkapp.pta_options import OPTGROUP_SYSTEM
from pytkapp.demo import demo_icons as demo_icons
from pytkapp.tkw import tkw_icons as tkw_icons

###################################
## classes
###################################
class DemoChildText(BaseChild):
    """child as word-processor"""

    def __init__(self, pw_container, po_app, **kw):
        """init"""

        self.__contentfile = None

        BaseChild.__init__(self, pw_container, po_app, **kw )

    def child_gui_reconf(self):
        """ reconf child gui controls """

        self.custom_reconf_title()

    def custom_reconf_title(self):
        """reconf title on some cases"""

        if self.__contentfile:
            lv_path, lv_file = os.path.split(self.__contentfile)

            self.set_title(lv_file)
        else:
            self.set_title(self.get_id())

    def call_clear_content(self, po_event=None):
        """call to clear content"""

        if self.child_askokcancel(_('Clear content ?')):
            self.clear_content()

    def clear_content(self):
        """clear content"""

        lw_content = self.get_resource_item('content')
        lw_content.clear_data()

        self.__contentfile = None

        self.family_gui_reconf()

    def call_open_content(self, po_event=None):
        """call to open content"""

        self.open_content()

    def open_content(self):
        """open content"""

        lw_content = self.get_resource_item('content')

        try:
            lv_path = lw_content.call_import_data()
            if lv_path:
                self.__contentfile = lv_path
        except:
            self.child_showerror(get_estr())
        finally:
            self.family_gui_reconf()

    def call_save_content(self, po_event=None):
        """call to save content"""

        self.save_content()

    def save_content(self):
        """save content"""

        lw_content = self.get_resource_item('content')

        try:
            lv_path = lw_content.call_export_data()
            if lv_path:
                self.__contentfile = lv_path
        except:
            self.child_showerror(get_estr())
        finally:
            self.family_gui_reconf()

    def get_description(self):
        """ return tuple (sb1,sb2,sb3) for app statusbar """

        if self.__contentfile:
            lv_sb1, lv_sb2 = os.path.split(self.__contentfile)
        else:
            lv_sb1 = 'w/o file'
            lv_sb2 = ''
        if self.thread_inuse():
            lv_sb3 = 'process: %s' % self.get_thread().getName()
        else:
            lv_sb3 = 'idle'

        return (lv_sb1, lv_sb2, lv_sb3)

    def child_create_widgets(self):
        """ fill child workspace """

        # sample of child workspace >>>
        lw_workspace = self.get_workspace()

        # tools >>>
        lw_toolframe = Frame(lw_workspace, bd=2, relief=RAISED)

        lw_btn = toolbar_button_generator(lw_toolframe, _('Clear'), tkw_icons.get_icon('gv_xscrolledtext_clear'), self.call_clear_content, padx=3, pady=3 )
        self.set_resource_item('toolbar_clearbtn', lw_btn)
        self.thread_set_unsafe_item('toolbar_clearbtn', lw_btn)

        toolbar_separator_generator(lw_toolframe)

        lw_btn = toolbar_button_generator(lw_toolframe, _('Open'), pta_icons.get_icon('gv_options_openfile'), self.call_open_content, padx=3, pady=3 )
        self.set_resource_item('toolbar_openbtn', lw_btn)
        self.thread_set_unsafe_item('toolbar_openbtn', lw_btn)

        lw_btn = toolbar_button_generator(lw_toolframe, _('Save'), pta_icons.get_icon('gv_icon_save'), self.call_save_content, padx=3, pady=3 )
        self.set_resource_item('toolbar_savebtn', lw_btn)
        self.thread_set_unsafe_item('toolbar_savebtn', lw_btn)

        lw_toolframe.pack(side=TOP, fill=X)

        # main content >>>
        lw_main = Frame(lw_workspace)

        lw_content = XScrolledText(lw_main,
                                      bg="white",
                                      defwidth=75,
                                      defheight=15,
                                      search=True,
                                      wstate=NORMAL,
                                      wrap=NONE)
        lw_content.pack(side=TOP, fill=BOTH, expand=YES)
        self.set_resource_item('content', lw_content)

        lw_main.pack(side=TOP, fill=BOTH, expand=YES)

        self.geom_propagate()

        self.otms_logger( {'type':'LOG', 'data':'Hello! I am alive !!!'} )
        self.otms_logger( {'type':'LOG', 'data':'My name id is "%s" and my title is "%s"!' % (self.get_id(), self.get_title())} )

        self.family_gui_reconf()

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        pass

    def child_gui_postinit(self):
        """ post-init routines for gui """

        pass

    def child_postinit(self):
        """ post init routines """

        # create child log embedded in application log
        lw_childlog = self.get_parentapp().app_create_child_log(self.get_id(), transpalette=False)
        # register widget for transparent logging
        self.set_resource_item('log', lw_childlog)
        # set title
        self.set_title('demo child %s' % self.get_id())

    def optwindow_prepare_optopts(self):
        """ return dict with options attrs for displaing """

        ld_optopts = {}

        ld_optopts['ch_border'] = {}
        ld_optopts['ch_border']['ro'] = True

        return ld_optopts

class DemoChildTable(BaseChild):
    """child as table-processor"""

    def __init__(self, pw_container, po_app, **kw):
        """init"""

        self.__contentfile = None

        BaseChild.__init__(self, pw_container, po_app, **kw )

    def child_gui_reconf(self):
        """ reconf child gui controls """

        self.custom_reconf_title()

    def custom_reconf_title(self):
        """reconf title on some cases"""

        if self.__contentfile:
            lv_path, lv_file = os.path.split(self.__contentfile)

            self.set_title(lv_file)
        else:
            self.set_title(self.get_id())

    def call_clear_content(self, po_event=None):
        """call to clear content"""

        if self.child_askokcancel(_('Clear content ?')):
            self.clear_content()

    def clear_content(self, noline=False):
        """clear content"""

        lw_content = self.get_resource_item('content')
        lw_content.clear_data()

        self.__contentfile = None

        if not noline:
            for i in range(255):
                lw_content.insert("end", '')

        lw_content.seecell('0,1')

        self.family_gui_reconf()

    def call_open_content(self, po_event=None):
        """call to open content"""

        self.open_content()

    def open_content(self):
        """open content"""

        lw_content = self.get_resource_item('content')
        lv_imppath = None

        try:
            lv_imppath = filedialog.askopenfilename(title=_('Import data'),
                                                    filetypes = {"%s {.%s}" % (_('Data'), 'csv'):0},
                                                    initialdir=os.getcwd(),
                                                    parent=self.get_mcontainer()
                                                   )
            lv_imppath = convert_fname( lv_imppath )

            if novl(lv_imppath, '') != '':
                lv_imppath = os.path.realpath(lv_imppath)

                lv_hdata = list(itertools.product('ABCDEF', repeat=2))
                lv_hlen = len(lv_hdata)

                self.clear_content(noline=True)

                flineindx = 0
                with codecs.open(lv_imppath, 'r', locale.getpreferredencoding()) as lo_f:
                    lb_headerfilled = False
                    for flineindx, fline in enumerate(lo_f):
                        if flineindx == 0:
                            continue
                        elif flineindx <= 255:
                            lt_data = tuple(fline.rstrip().split(';')[1:lv_hlen+1])

                            lw_content.insert_data("end", ('',)+lt_data)
                        else:
                            flineindx += 1

                if flineindx < 255:
                    for i in range(flineindx, 255):
                        lw_content.insert("end", '')

                lw_content.seecell('0,1')

                self.__contentfile = lv_imppath
        except:
            self.child_showerror(get_estr())
        finally:
            self.family_gui_reconf()

    def call_save_content(self, po_event=None):
        """call to save content"""

        self.save_content()

    def save_content(self):
        """save content"""

        lw_content = self.get_resource_item('content')
        try:
            lv_path = lw_content.call_export()
            if lv_path:
                self.__contentfile = lv_path
        except:
            self.child_showerror(get_estr())
        finally:
            self.family_gui_reconf()

    def get_description(self):
        """ return tuple (sb1,sb2,sb3) for app statusbar """

        if self.__contentfile:
            lv_sb1, lv_sb2 = os.path.split(self.__contentfile)
        else:
            lv_sb1 = 'w/o file'
            lv_sb2 = ''

        if self.thread_inuse():
            lv_sb3 = 'process: %s' % self.get_thread().getName()
        else:
            lv_sb3 = 'idle'

        return (lv_sb1, lv_sb2, lv_sb3)

    def child_create_widgets(self):
        """ fill child workspace """

        # sample of child workspace >>>
        lw_workspace = self.get_workspace()

        # tools >>>
        lw_toolframe = Frame(lw_workspace, bd=2, relief=RAISED)

        lw_btn = toolbar_button_generator(lw_toolframe, _('Clear'), tkw_icons.get_icon('gv_xscrolledtext_clear'), self.call_clear_content, padx=3, pady=3 )
        self.set_resource_item('toolbar_clearbtn', lw_btn)
        self.thread_set_unsafe_item('toolbar_clearbtn', lw_btn)

        toolbar_separator_generator(lw_toolframe)

        lw_btn = toolbar_button_generator(lw_toolframe, _('Open'), pta_icons.get_icon('gv_options_openfile'), self.call_open_content, padx=3, pady=3 )
        self.set_resource_item('toolbar_openbtn', lw_btn)
        self.thread_set_unsafe_item('toolbar_openbtn', lw_btn)

        lw_btn = toolbar_button_generator(lw_toolframe, _('Save'), pta_icons.get_icon('gv_icon_save'), self.call_save_content, padx=3, pady=3 )
        self.set_resource_item('toolbar_savebtn', lw_btn)
        self.thread_set_unsafe_item('toolbar_savebtn', lw_btn)

        lw_toolframe.pack(side=TOP, fill=X)

        # main content >>>
        lw_main = Frame(lw_workspace)

        lv_hdata = list(itertools.product('ABCDEF', repeat=2))
        lv_hlen = len(lv_hdata)

        lt_headers = ( 0, 'Row', )
        for colname in lv_hdata:
            lt_headers += ( 0, colname, )

        lw_content = EXTableList(lw_main,
                                 activestyle="none",
                                 background = "white",
                                 columns = lt_headers,
                                 selecttype="row",
                                 selectmode="single", #single, browse, multiple, extended
                                 stretch = "all",
                                 stripebackground="gray90",
                                 height=15,
                                 width=75,
                                 titlecolumns=1,
                                 showseparators=True,
                                 # additional
                                 allowtledit=True,
                                 allowresize=True,
                                 hscroll=True,
                                 vscroll=True
                                 )
        lw_content.xcontent()
        lw_content.columnconfigure(0, showlinenumbers=True)
        lw_content.pack(side=TOP, fill=BOTH, expand=YES)
        self.set_resource_item('content', lw_content)

        for i in range(1, lv_hlen+1):
            lw_content.columnconfigure(i, editable=True)

        for i in range(255):
            lw_content.insert("end", '')

        lw_main.pack(side=TOP, fill=BOTH, expand=YES)

        self.geom_propagate()

        self.otms_logger( {'type':'LOG', 'data':'Hello! I am alive !!!'} )
        self.otms_logger( {'type':'LOG', 'data':'My name id is "%s" and my title is "%s"!' % (self.get_id(), self.get_title())} )

        self.family_gui_reconf()

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        pass

    def child_gui_postinit(self):
        """ post-init routines for gui """

        pass

    def child_postinit(self):
        """ post init routines """

        # create child log embedded in application log
        lw_childlog = self.get_parentapp().app_create_child_log(self.get_id(), transpalette=False)
        # register widget for transparent logging
        self.set_resource_item('log', lw_childlog)
        # set title
        self.set_title('demo child %s' % self.get_id())

    def optwindow_prepare_optopts(self):
        """ return dict with options attrs for displaing """

        ld_optopts = {}

        ld_optopts['ch_border'] = {}
        ld_optopts['ch_border']['ro'] = True

        return ld_optopts

class DemoChildTH( BaseChild ):
    """ child"""

    def __init__( self, pw_container, po_app, **kw ):
        """ init child """

        # generate single option for child
        ll_options = []
        ll_options.append( {'name':'ch_border',
                            'type':'int',
                            'default':50,
                            'reset':1,
                            'export':0,
                            'wstyle':'Spinbox',
                            'min':1,
                            'max':100,
                            'step':1,
                            'cdata':None,
                            'group':_('Child'),
                            'desc':_('Iterations')
                            } )
        kw['optionsdata'] = ll_options

        BaseChild.__init__(self, pw_container, po_app, **kw )

    def demo_change_title(self):
        """ demo """

        lw_entry = self.get_resource_item('entry')
        lv_value = lw_entry.get()

        if novl(lv_value,'').strip() != '':
            self.set_title(lv_value)

            self.otms_logger( {'type':'LOG', 'data':'Now my title is "%s"!' % (self.get_title(),)} )

    def demo_add_logtag(self, po_event=None):
        """ demo """

        lw_entry = self.get_resource_item('entry')
        lv_value = lw_entry.get()

        if novl(lv_value,'').strip() != '':
            lw_log = self.get_resource_item('log')
            if lw_log:
                lw_log.storedatawidgetendl1mark('pos1')

                self.child_logging(lv_value)

                lw_log.tag_data(lv_value, 'pos1')

    def demo_call_nwtoplevel(self):
        """call non-waiting toplevel"""

        lw_entry = self.get_resource_item('entry')
        lv_value = lw_entry.get()

        if novl(lv_value,'').strip() != '':
            lw_toplevel, lw_topframe = toplevel_header(self.get_mcontainer(),
                                                       title='Non waiting toplevel "%s"'% lv_value
                                                      )

            Button(lw_topframe, text='Close me', command=lw_toplevel.destroy, padx=10, pady=10).pack()

            toplevel_footer(lw_toplevel, self.get_mcontainer(), nowait=True, nograb=True)

            self.child_add_nowaittoplevel(lw_toplevel)

    def demo_call_subchild(self):
        """ demo """

        lw_entry = self.get_resource_item('entry')
        lv_value = lw_entry.get()

        if novl(lv_value,'').strip() != '':
            self.call_subchild_add(lv_value, 'sub-child (%s)' % (lv_value), DemoSubChild)

    def demo_remove_help(self):
        """ demo """

        self.set_help([])

    def demo_add_help(self):
        """ demo """

        lw_log = self.get_resource_item('log')
        self.set_help(lw_log.get_data().split('\n'))

    def demo_add_xhelp(self):
        """ demo """

        lv_file = filedialog.askopenfilename()
        if lv_file:
            self.set_help('@%s' % lv_file)

    def demo_call_process_start(self):
        """ demo """

        if self.child_askokcancel(_('Start demo process ?')):
            self.process_start('Demo', self.demo_process)

    def demo_call_process_stop(self):
        """ demo """

        if self.child_askokcancel(_('Stop demo process ?')):
            self.process_stop()

    def demo_call_options(self):
        """call child options"""

        self.call_options_window()

    def demo_process(self):
        """ demo """

        self.otms_logger( {'type':'LOG', 'data':'process: begin'} )

        lv_counter = 0

        lv_border = self.options_get_value('ch_border')

        while lv_counter < lv_border:
            lv_counter += 1

            if lv_counter % 10 == 0:
                self.otms_logger( {'type':'LOG', 'data':'process %s/%s' % (lv_counter, lv_border)} )

            if self.get_stop_event().is_set():
                self.otms_logger( {'type':'LOG', 'data':'process was broken on %s/%s' % (lv_counter, lv_border)} )
                break

            time.sleep(0.5)

        self.otms_logger( {'type':'LOG', 'data':'process: end'} )

        # use this message to set thread = None
        self.otms_logger( {'type':'PROCESS_END', 'data':None} )

    def demo_childmessages(self, po_event=None):
        """demo of child messages"""

        ld_params = {}
        ll_variants = []
                            # text, tooltip, icon, value
        ll_variants.append( ('Info', 'Show info box', None, '<info>',) )
        ll_variants.append( ('Warning', 'Show warning box', None, '<warning>',) )
        ll_variants.append( ('Error', 'Show error box', None, '<error>',) )
        ll_variants.append( ('<separator>', ))
        ll_variants.append( ('YesNo', 'Show yes/no box', None, '<yesno>',) )
        ll_variants.append( ('YesNoCancel', 'Show yes/no/cancel box', None, '<yesnocancel>',) )
        ll_variants.append( ('OkCancel', 'Show ok/cancel box', None, '<okcancel>',) )

        ld_params['variants'] = ll_variants
        ld_params['title'] = 'Select variant'
        ld_params['detail'] = 'Some details here'
        lo_dialog = BaseSelector(self.get_workspace(),
                                 **ld_params
                                )
        lv_result = lo_dialog.show(width=200, height=300, wal=True)
        if lv_result is None:
            self.child_showinfo('Variant was not selected !')
        elif lv_result == '<info>':
            self.child_showinfo(_('Some info'), detail=_('Any details'))
        elif lv_result == '<warning>':
            self.child_showwarning(_('Some warning'), detail=_('Any details'))
        elif lv_result == '<error>':
            self.child_showerror(_('Some error'), detail=_('Any details'))
        elif lv_result == '<yesno>':
            self.child_askyesno(_('Some question'), detail=_('Any details'))
        elif lv_result == '<okcancel>':
            self.child_askokcancel(_('Some proposal'), detail=_('Any details'))
        elif lv_result == '<yesnocancel>':
            self.child_askyesnocancel(_('Some alternatives'), detail=_('Any details'))

    def demo_childroutines(self, po_event=None):
        """ call selector for routines that can be applyed on child itself"""

        ld_params = {}
        ll_variants = []
                            # text, tooltip, icon, value
        ll_variants.append( ('Change title', 'Change title from text field', None, '<title>',) )
        ll_variants.append( ('<separator>', ))

        ll_variants.append( ('Make custom tag for log', 'Add to text custom tag from text field', None, '<logtag>',) )
        ll_variants.append( ('<separator>', ))

        ll_variants.append( ('Add help as list from log', 'Fill help data from process log and make it available', None, '<addhelp>',) )
        ll_variants.append( ('Add help as external file', 'Link external file as help file', None, '<addxhelp>',) )
        ll_variants.append( ('Remove help', 'Clear help data and remove controls', None, '<delhelp>',) )

        ld_params['variants'] = ll_variants
        ld_params['title'] = 'Select variant'
        ld_params['detail'] = 'Some details here'
        lo_dialog = BaseSelector(self.get_workspace(),
                                 **ld_params
                                )
        lv_result = lo_dialog.show(width=200, height=300, wal=True)
        if lv_result is None:
            self.child_showinfo('Variant was not selected !')
        elif lv_result == '<title>':
            self.demo_change_title()
        elif lv_result == '<logtag>':
            self.demo_add_logtag()
        elif lv_result == '<addhelp>':
            self.demo_add_help()
        elif lv_result == '<addxhelp>':
            self.demo_add_xhelp()
        elif lv_result == '<delhelp>':
            self.demo_remove_help()
        else:
            self.child_showinfo('Variant: %s' % lv_result)

    def demo_subroutines(self, po_event=None):
        """ call selector for routines that can be applyed on subchild and etc."""

        ld_params = {}

        ll_variants = []

                            # text, tooltip, icon, value
        ll_variants.append( ('Create sub-child', 'Create sub-child', None, '<subchild>',) )
        ll_variants.append( ('Create NW-toplevel', 'Create non-waiting toplevel', None, '<nw>',) )

        ld_params['variants'] = ll_variants
        ld_params['title'] = 'Select variant'
        ld_params['detail'] = 'Some details here'
        lo_dialog = BaseSelector(self.get_workspace(),
                                 **ld_params
                                )
        lv_result = lo_dialog.show(width=200, height=300, wal=True)
        if lv_result is None:
            self.child_showinfo('Variant was not selected !')
        elif lv_result == '<subchild>':
            self.demo_call_subchild()
        elif lv_result == '<nw>':
            self.demo_call_nwtoplevel()
        else:
            self.child_showinfo('Variant: %s' % lv_result)

    def child_gui_reconf(self):
        """ reconf child gui controls """

        pass

    def child_create_widgets(self):
        """ fill child workspace """

        # sample of child workspace >>>
        lw_workspace = self.get_workspace()

        # tools >>>
        lw_toolframe = Frame(lw_workspace, bd=2, relief=RAISED)

        lw_optbtn = toolbar_button_generator(lw_toolframe, _('Options'), pta_icons.get_icon('gv_app_options'), self.demo_call_options, padx=3, pady=3 )
        self.set_resource_item('toolbar_optbtn', lw_optbtn)
        self.thread_set_unsafe_item('toolbar_optbtn', lw_optbtn)

        toolbar_separator_generator(lw_toolframe)

        lw_toolframe.pack(side=TOP, fill=X)


        lw_frame1 = Frame(lw_workspace)

        lw_label = Label(lw_frame1, text='Type some text here:')
        lw_label.grid(row=0, column=0, padx=2, pady=2)

        lw_entry = Entry(lw_frame1)
        lw_entry.grid(row=0, column=1, columnspan=3, padx=2, pady=2, sticky=N+E+W+S)
        self.set_resource_item('entry', lw_entry)

        lw_frame1.columnconfigure( 1, weight=1 )
        lw_frame1.pack(side=TOP, fill=X)

        lw_frame2 = LabelFrame(lw_workspace, text='Routines for:')

        lw_btn = Button(lw_frame2, text='Messages', command=self.demo_childmessages)
        lw_btn.pack(side=LEFT, padx=2, pady=2)

        lw_btn = Button(lw_frame2, text='Child', command=self.demo_childroutines)
        lw_btn.pack(side=LEFT, padx=2, pady=2)

        lw_btn = Button(lw_frame2, text='Sub-elements', command=self.demo_subroutines)
        lw_btn.pack(side=LEFT, padx=2, pady=2)

        lw_frame2.pack(side=TOP, fill=X)

        lw_frame3 = LabelFrame(lw_workspace, text='Threads')

        b1 = Button(lw_frame3, text='Start process', command=self.demo_call_process_start)
        b1.grid(row=0, column=0, padx=2, pady=2, sticky=N+E+W+S)
        self.set_resource_item('thstart_btn', b1)
        self.thread_set_unsafe_item('thstart_btn', b1)

        b2 = Button(lw_frame3, text='Stop process', command=self.demo_call_process_stop, state=DISABLED)
        b2.grid(row=0, column=2, padx=2, pady=2, sticky=N+E+W+S)
        self.set_resource_item('thstop_btn', b2)
        self.thread_set_safe_item('thstop_btn', b2)

        lw_frame3.pack(side=TOP, fill=X)

        self.geom_propagate()

        self.otms_logger( {'type':'LOG', 'data':'Hello! I am alive !!!'} )
        self.otms_logger( {'type':'LOG', 'data':'My name id is "%s" and my title is "%s"!' % (self.get_id(), self.get_title())} )

        self.family_gui_reconf()

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        pass

    def child_gui_postinit(self):
        """ post-init routines for gui """

        pass

    def child_postinit(self):
        """ post init routines """

        # create child log embedded in application log
        lw_childlog = self.get_parentapp().app_create_child_log(self.get_id(), transpalette=False)
        # register widget for transparent logging
        self.set_resource_item('log', lw_childlog)
        # set title
        self.set_title('demo child %s' % self.get_id())

    def optwindow_prepare_optopts(self):
        """ return dict with options attrs for displaing """

        ld_optopts = {}

        ld_optopts['ch_border'] = {}
        ld_optopts['ch_border']['ro'] = True

        return ld_optopts

class DemoSubChild( BaseChild ):
    """ another variant of child """

    def __init__(self, pw_container, po_app, **kw):
        """ initialization of subchild """

        BaseChild.__init__(self, pw_container, po_app,
                           parentw=kw.get( 'parentw', None ),
                           childid=kw.get( 'childid', 'window' ),
                           title=kw.get( 'title', '' ),
                           mw=kw.get( 'mw', 250 ),
                           mh=kw.get( 'mh', 100 ),
                           icon=kw.get( 'icon', pta_icons.get_icon('gv_subchild_header_icon') ) )

    def child_create_widgets(self):
        """ fill child workspace """

        lw_btn = Button( self.get_workspace(), text='Print Hello', command=self.demo_print_hello)
        lw_btn.pack(side=LEFT, anchor=NW)

        lw_btn = Button( self.get_workspace(), text='Log Hello', command=self.demo_log_hello)
        lw_btn.pack(side=LEFT, anchor=NW)

        lw_parent = self.get_parentwidget()
        if lw_parent:
            lb_at = True
        else:
            lb_at = False

        self.otms_logger( {'type':'LOG', 'data':'Hello! I am alive too !!!', 'at':lb_at} )
        if lw_parent:
            lv_parentid = lw_parent.get_id()
            lv_parenttitle = lw_parent.get_title()
            self.otms_logger( {'type':'LOG', 'data':'I am sub-child of "%s" that titled "%s"' % (lv_parentid, lv_parenttitle,), 'at':lb_at} )
        self.otms_logger( {'type':'LOG', 'data':'My name id is "%s" and my title is "%s"!' % (self.get_id(), self.get_title()), 'at':lb_at} )

    def child_gui_reconf(self):
        """ reconf child gui controls """

        pass

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        pass

    def demo_print_hello(self):
        """just print hello"""

        lv_message = '%s: hello !!!' % self.get_id()
        print(lv_message)

    def demo_log_hello(self):
        """just print hello"""

        lv_message = '%s: hello !!!' % self.get_id()
        self.child_logging(lv_message)

    def child_gui_postinit(self):
        """ post-init routines for gui """

        pass

    def child_postinit(self):
        """ post init routines """

        pass

class DemoApp( BaseApp ):
    """ demo application"""

    def __init__(self, p_root, **kw):
        """ init app """

        BaseApp.__init__(self, p_root, **kw)

        lw_log = self.get_logwidget()
        if lw_log is not None:
            go_greedlogger.add_outmethod( threading.current_thread().ident,
                                          lambda message: lw_log.insert_data(message,True)
                                        )
        else:
            go_greedlogger.add_outmethod( threading.current_thread().ident, 'print' )

    def app_generate_title(self):
        """ generate string for app title and return it """

        return pytkapp_info.get_deftitle()

    def get_default_child_class(self):
        """ get default child class """

        return DemoChildTH

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        pass

    def app_reconf_menu(self, **kw):
        """ reconf state of menu items """

        pass

    def toolbar_create_draft(self):
        """ prepare control data of toolbar items """

        ld_draft = {}
        self.set_resource_item('toolbar_draft', ld_draft)

        ld_draft['textchild_btn']  = {'label':_("TextChild"), 'type':'button'}
        ld_draft['tablechild_btn'] = {'label':_("TableChild"), 'type':'button'}
        ld_draft['thchild_btn']    = {'label':_("ThreadChild"), 'type':'button'}

        ld_draft['close_btn']    = {'label':_("Close"),     'type':'button'}
        ld_draft['cascade_btn']  = {'label':_("Cascade"),   'type':'button'}
        ld_draft['tile_btn']     = {'label':_("Tile"),      'type':'button'}
        ld_draft['closeall_btn'] = {'label':_("Close all"), 'type':'button'}
        ld_draft['overview_btn'] = {'label':_("Overview"),  'type':'button'}

        ld_draft['togglelog_btn'] = {'label':_("Hide log pane"), 'type':'button'}

    def toolbar_initconf(self):
        """ toolbar filling """

        self.toolbar_create_draft()

        if self.get_useapplog():
            self.toolbar_create_lbtns()
            self.get_root().bind('<F12>', self.call_app_toggle_logpane, '+')
            self.get_root().bind('<F11>', self.call_app_children_overview, '+')

        if self.get_uimode() == APP_UI_MODE_MDI:
            self.toolbar_create_custombtns()
            self.toolbar_create_wbtns(add=False)

    def app_reconf_toolbar(self, **kw):
        """ reconf state of toolbar controls """

        lw_btn = self.get_gui_std_item('wtoolbar_textchild')
        if lw_btn:
            lw_btn.configure(state=NORMAL)
        lw_btn = self.get_gui_std_item('wtoolbar_tablechild')
        if lw_btn:
            lw_btn.configure(state=NORMAL)
        lw_btn = self.get_gui_std_item('wtoolbar_thchild')
        if lw_btn:
            lw_btn.configure(state=NORMAL)

    def toolbar_create_custombtns(self):
        """ toolbar filling """

        ld_toolbar_draft = self.get_resource_item('toolbar_draft')

        # add window
        lw_toolframe = Frame( self.get_toolbar(), padx=2, pady=2 )
        self.set_gui_std_item( 'wtoolbar_customframe', lw_toolframe )


        item = toolbar_lbutton_generator(lw_toolframe, ld_toolbar_draft['textchild_btn']['label'], demo_icons.get_icon('gv_icon_demo_word'), DISABLED, lambda x=1: self.call_app_child_add(DemoChildText))
        self.set_gui_std_item( 'wtoolbar_textchild', item )

        item = toolbar_lbutton_generator(lw_toolframe, ld_toolbar_draft['tablechild_btn']['label'], demo_icons.get_icon('gv_icon_demo_excel'), DISABLED, lambda x=1: self.call_app_child_add(DemoChildTable))
        self.set_gui_std_item( 'wtoolbar_tablechild', item )

        item = toolbar_lbutton_generator(lw_toolframe, ld_toolbar_draft['thchild_btn']['label'], demo_icons.get_icon('gv_icon_demo_lightning'), DISABLED, lambda x=1: self.call_app_child_add(DemoChildTH))
        self.set_gui_std_item( 'wtoolbar_thchild', item )

        toolbar_separator_generator(lw_toolframe)

        lw_toolframe.pack(side=LEFT)

    def app_child_generator(self, child_id, class_):
        """ create instance of class_ object and fill it ui """

        lw_child   = None
        lv_title   = ''

        ll_options = []
        ll_rulesdata = []
        lv_icon    = ''

        if class_ == DemoChildText:
            lv_icon = demo_icons.get_icon('gv_icon_demo_word')
            lv_title = _('Demo Text')
            lv_logopath, lv_logoname = self.get_logos_data(class_)
        elif class_ == DemoChildTable:
            lv_icon = demo_icons.get_icon('gv_icon_demo_excel')
            lv_title = _('Demo Table')
            lv_logopath, lv_logoname = self.get_logos_data(class_)
        elif class_ == DemoChildTH:
            lv_icon = demo_icons.get_icon('gv_icon_demo_lightning')
            lv_title = _('Demo TH')
            lv_logopath, lv_logoname = self.get_logos_data(class_)
        else:
            self.app_showerror(_('Invalid class'),
                               detail='%s'%class_)
            return None

        # check access
        lb_access = True

        if lb_access:
            lw_child = class_( self.get_workspace(), self,
                               childid = child_id,
                               title = lv_title,
                               logopath=lv_logopath,
                               logoname=lv_logoname,
                               icon = lv_icon,
                               optionsdata = ll_options,
                               rulesdata = ll_rulesdata
                               )
        else:
            self.app_showwarning(_('Permission denied to use this object: "%s"') % lv_title)

        if lw_child is not None:
            lw_child.child_gui_init()

        return lw_child

    def app_postinit(self):
        """post init"""

        self.app_reconf_toolbar()

###################################
## routines
###################################
def run_demo():
    """ main """

    print_envdata()

    ### splash
    # prepare parameters for application's splash window
    ld_splash = {}
    ld_splash['appname']  = pytkapp_info.get_appname()
    ld_splash['appver']   = '%s' % (pytkapp_info.get_appversion_t(),)
    ld_splash['appurl']   = pytkapp_info.get_appurl()
    ld_splash['bg']  = 'white'
    ld_splash['fg']  = 'black'
    ld_splash['bd1'] = 1
    ld_splash['bd2'] = 1

    # OR use splashdata=None (OR call app without splashdata keyword)
    #ld_splash = None

    ### options
    # prepare options for application
    ll_options = []
    ll_options.append( {'name':'demovalue1',
                        'type':'int',
                        'default':20,
                        'reset':1,
                        'export':0,
                        'wstyle':'Spinbox',
                        'min':1,
                        'max':50,
                        'step':1,
                        'cdata':None,
                        'group':_('Demo'),
                        'desc':_('Demo value 1')
                        } )
    ll_options.append( {'name':'demovalue2',
                        'type':'int',
                        'default':3,
                        'reset':1,
                        'export':0,
                        'wstyle':'Spinbox',
                        'min':1,
                        'max':5,
                        'step':1,
                        'cdata':None,
                        'group':_('Demo'),
                        'desc':_('Demo value 2')
                        } )

    # OR use optionsdata=None (OR call app without optionsdata keyword)
    #ll_options = None

    # if you use options - than you can specify rules
    ll_rulesdata = []
    ll_rulesdata.append( ('demovalue1',  # when for option
                          'value>', # it value will be more than
                          10, # 20
                          'demovalue2', # then this options
                          'value', # will be setted to
                          5
                          ) )
    ll_rulesdata.append( ('demovalue1',  # when for option
                          'value<=', # it value will be less (or equal) than
                          10, # 20
                          'demovalue2', # then this options
                          'value', # will be setted to
                          3
                          ) )

    # OR use rulesdata=None (OR call app without rulesdata keyword)
    #ld_rulesdata = None

    ### threads
    # set usethreads = True to call routines from child in threads
    lb_usethreads = True

    # OR set usetgreads=False (OR dont use usethreads keyword)
    #lb_usethreads = False

    ### log
    # set useapplog to True and app will contain Xscrolledtext as log
    lb_useapplog = True
    # OR set it to False (OR dont use it)
    #lb_useapplog = False

    ### about info
    # set aboutlist - app will be display about menu
    ll_aboutlist = []
    ll_aboutlist.append('Here is a sample of about text')
    ll_aboutlist.append('another line...')

    # OR set ll_aboutlist=None (OR dont use aboutlist keyword)
    #ll_aboutlist=None

    try:
        print('Init application...')
        lo_app = DemoApp( None,
                          uimode=APP_UI_MODE_MDI,
                          splashdata=ld_splash,
                          optionsdata=ll_options,
                          rulesdata=ll_rulesdata,
                          usethreads=lb_usethreads,
                          aboutlist=ll_aboutlist,
                          useapplog=lb_useapplog,
                          minwidth=800,
                          minheight=600 )

        print('Run application...')
        lo_app.run()
    except:
        print('run-time error:%s'%(get_estr()))

if __name__ == '__main__':
    run_demo()
