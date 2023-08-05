#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for SDI app """

# pytkapp: demo for SDI app
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

pytkapp_info.__appname__ = 'PyTkApp SDI Demo'
pytkapp_info.__appdesc__ = 'PyTkApp SDI Demo'

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
import subprocess
import locale

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
    from tkinter.constants import YES, BOTH, X, N, S, W, E, LEFT, DISABLED, NORMAL, RAISED, TOP, END, BOTTOM
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Entry
    from Tkinter import Label, LabelFrame, Frame, Button
    from Tkconstants import YES, BOTH, X, N, S, W, E, LEFT, DISABLED, NORMAL, RAISED, TOP, END, BOTTOM
    import tkMessageBox as messagebox

import pytkapp.pta_icons as pta_icons
from pytkapp.tkw.tkw_routines import make_widget_resizeable, READONLY
from pytkapp.tkw.tkw_routines import toolbar_button_generator, toolbar_separator_generator
from pytkapp.tkw.tkw_xscrolledtext import XScrolledText
import pytkapp.tkw.tkw_icons as tkw_icons

from pytkapp.dia.dia_selector import BaseSelector
from pytkapp.pta_options import OPTGROUP_SYSTEM
from pytkapp.pta_child import BaseChild
from pytkapp.pta_constants import CHILD_UI_MODE_SDI
from pytkapp.pta_app import BaseApp
from pytkapp.pta_constants import APP_UI_MODE_SDI
from pytkapp.pta_routines import print_envdata, get_estr

###################################
## classes
###################################
class DemoChild( BaseChild ):
    """ child"""

    def __init__( self, pw_container, po_app, **kw ):
        """ init child """

        self.__prevcmd = None

        BaseChild.__init__(self, pw_container, po_app, **kw )

    def child_gui_reconf(self):
        """ reconf child gui controls """

        pass

    def call_execute(self, po_event=None):
        """call to execute"""

        lw_centry = self.get_resource_item('entry')
        lv_text = lw_centry.get().rstrip()

        if lv_text != '' and self.child_askokcancel('Execute command ?',
                                                    detail=lv_text):
            self.execute_()

    def clear_(self):
        """call clear"""

        lw_widget = self.get_resource_item('content')
        lw_widget.call_clear_data()

    def export_(self):
        """call export"""

        lw_widget = self.get_resource_item('content')
        lw_widget.call_export_data()

    def execute_(self):
        """execute command"""

        lw_centry = self.get_resource_item('entry')
        lw_content = self.get_resource_item('content')
        lv_text = lw_centry.get().rstrip()

        p = None
        lv_preerr = None
        lo_startupinfo = subprocess.STARTUPINFO()
        lo_startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            if sys.platform == 'win32':
                p = subprocess.Popen(lv_text.split(' '),
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     startupinfo=lo_startupinfo)
            else:
                p = subprocess.Popen(lv_text.split(' '),
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
        except OSError as exp:
            lv_preerr = '%s: %s' % (exp, exp.message,)
            p = None

        try:
            if not p:
                if sys.platform == 'win32':
                    p = subprocess.Popen(lv_text.split(' '),
                                         stderr=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         startupinfo=lo_startupinfo,
                                         shell=True)
                else:
                    p = subprocess.Popen(lv_text.split(' '),
                                         stderr=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         shell=True)
            p.wait()
            ll_answer = []

            while True:
                lv_line = p.stdout.readline()
                if not lv_line:
                    break
                else:
                    if sys.platform == 'win32':
                        lv_line = lv_line.decode('cp866')
                    else:
                        lv_line = lv_line.decode(locale.getpreferredencoding())

                    ll_answer.append(lv_line.rstrip())

            if not ll_answer:
                ll_answer.append(lv_preerr)

            lv_answer = '\n'.join(ll_answer)
            lv_answer += '\n'

            self.__prevcmd = lv_text
            lw_content.insert_data(lv_answer, see_=True)
            lw_content.insert_data('---\n', see_=True)
        except:
            self.child_showerror(get_estr())
        finally:
            self.child_logging('+++', pb_at=False)
            lw_centry.delete(0, END)

    def call_prev_cmd(self, po_event=None):
        """fill prev command"""

        if self.__prevcmd:
            lw_centry = self.get_resource_item('entry')
            lw_centry.delete(0, END)
            lw_centry.insert(0, self.__prevcmd)

    def child_create_widgets(self):
        """ fill child workspace """

        # sample of child workspace >>>
        lw_workspace = self.get_workspace()

        lw_cframe = Frame(lw_workspace)

        lw_label = Label(lw_cframe, text='Command')
        lw_label.pack(side=LEFT)

        lw_entry = Entry(lw_cframe)
        lw_entry.pack(side=LEFT, fill=X, expand=YES)
        lw_entry.bind('<Return>', self.call_execute)
        lw_entry.bind('<Up>', self.call_prev_cmd)
        self.set_resource_item('entry', lw_entry)

        lw_runbtn = Button(lw_cframe, text='Run', command=self.call_execute)
        lw_runbtn.pack(side=LEFT, padx=2, pady=2)

        lw_cframe.pack(side=TOP, fill=X)

        lw_demowidget = XScrolledText(lw_workspace,
                                      bg='#000000',
                                      fg='#ffffff',
                                      cursor="arrow",
                                      defwidth=70,
                                      defheight=5,
                                      search=True,
                                      clear=True,
                                      unload=True,
                                      wstate=READONLY)

        lw_demowidget.pack(side=TOP, fill=BOTH, expand=YES)
        self.set_resource_item('content', lw_demowidget)

        self.geom_propagate()
        self.otms_logger( {'type':'LOG', 'data':'I am alive !!!'} )
        self.family_gui_reconf()

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        pass

    def child_gui_postinit(self):
        """ post-init routines for gui """

        lw_entry = self.get_resource_item('entry')
        lw_entry.focus_set()

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

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        pass

    def app_generate_title(self):
        """ generate string for app title and return it """

        return pytkapp_info.get_deftitle()

    def app_postinit(self):
        """ post init routines - use it for SDI app (see demo) """

        if self.get_uimode() == APP_UI_MODE_SDI:
            self.call_app_child_add(DemoChild)

    def get_default_child_class(self):
        """ get default child class """

        return DemoChild

    def get_default_child_uimode(self):
        """ return default mode of child's ui """

        return CHILD_UI_MODE_SDI

    def app_reconf_menu(self, **kw):
        """ reconf state of menu items """

        pass

    def app_reconf_toolbar(self, **kw):
        """ reconf state of toolbar controls """

        pass

    def toolbar_create_draft(self):
        """ prepare control data of toolbar items """

        ld_draft = {}
        self.set_resource_item('toolbar_draft', ld_draft)

        ld_draft['togglelog_btn']     = {'label':_("Hide log pane"), 'type':'button'}

        ld_draft['clearcontent_btn']  = {'label':_("Clear"), 'type':'button'}
        ld_draft['exportcontent_btn'] = {'label':_("Export"), 'type':'button'}

    def toolbar_initconf(self):
        """ toolbar filling """

        self.toolbar_create_draft()

        if self.get_useapplog():
            self.toolbar_create_lbtns()
            self.get_root().bind('<F12>', self.call_app_toggle_logpane, '+')

        self.toolbar_create_custombtns()

    def call_ac_clear(self, po_event=None):
        """call clear of content in active child"""

        lo_child = self.get_active_child()
        lo_child.clear_()

    def call_ac_export(self, po_event=None):
        """call export of content in active child"""

        lo_child = self.get_active_child()
        lo_child.export_()

    def toolbar_create_custombtns(self):
        """ toolbar filling """

        ld_toolbar_draft = self.get_resource_item('toolbar_draft')

        # add window
        lw_toolframe = Frame( self.get_toolbar(), padx=2, pady=2 )
        self.set_gui_std_item( 'wtoolbar_customframe', lw_toolframe )

        item = toolbar_button_generator(lw_toolframe, ld_toolbar_draft['clearcontent_btn']['label'], tkw_icons.get_icon('gv_xscrolledtext_clear'), self.call_ac_clear)
        self.set_gui_std_item( 'wtoolbar_clearcontent', item )

        item = toolbar_button_generator(lw_toolframe, ld_toolbar_draft['exportcontent_btn']['label'], tkw_icons.get_icon('gv_xscrolledtext_export'), self.call_ac_export)
        self.set_gui_std_item( 'wtoolbar_exportcontent', item )

        lw_toolframe.pack(side=LEFT)

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
                          uimode=APP_UI_MODE_SDI,
                          splashdata=ld_splash,
                          optionsdata=ll_options,
                          rulesdata=ll_rulesdata,
                          usethreads=lb_usethreads,
                          aboutlist=ll_aboutlist,
                          useapplog=lb_useapplog,
                          minwidth=640,
                          minheight=480 )

        print('Run application...')
        lo_app.run()
    except:
        print('run-time error:%s'%(get_estr()))

if __name__ == '__main__':
    run_demo()
