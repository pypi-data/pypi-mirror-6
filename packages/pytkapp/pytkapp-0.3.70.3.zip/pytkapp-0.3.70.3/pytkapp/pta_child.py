#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" child base class """

# pytkapp: child base class
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
import time
import gettext

if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    import queue as queue
    #from tkinter import StringVar, Widget, TclError
    #from tkinter import PhotoImage
    #from tkinter import Label, Frame, Button, Toplevel
    #from tkinter.constants import DISABLED, NORMAL, N, S, W, E, YES, LEFT, RIGHT, TOP, BOTH, X, FLAT, RAISED, SUNKEN, END
    #import tkinter.messagebox as messagebox
    #import tkinter.scrolledtext as scrolledtext
else:
    import Queue as queue
    #from Tkinter import StringVar, Widget, TclError
    #from Tkinter import PhotoImage
    #from Tkinter import Label, Frame, Button, Toplevel
    #from Tkconstants import DISABLED, NORMAL, N, S, W, E, YES, LEFT, RIGHT, TOP, BOTH, X, FLAT, RAISED, SUNKEN, END
    #import tkMessageBox as messagebox
    #import ScrolledText as scrolledtext

import threading

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.tkw.tkw_xtk import *
from cpr_tkinter import StringVar, Widget, TclError, PhotoImage, Label, Frame, Button, Toplevel
from cpr_tkconstants import DISABLED, NORMAL, N, S, W, E, YES, LEFT, RIGHT, TOP, BOTH, X, FLAT, RAISED, SUNKEN, END
import cpr_tkmessagebox as messagebox
import cpr_tkscrolledtext as scrolledtext

import pytkapp.pta_icons as pta_icons

from pytkapp.pta_thread import DummyThread
from pytkapp.pta_routines import open_file, get_estr, novl, xprint, get_logtime, Others

from pytkapp.pta_options import OptionsContainer, OptionError
from pytkapp.pta_options import OPTIONS_UI_MODE_TK, OPTIONS_UI_MODE_NOTK, OPTGROUP_UNASSIGNED
from pytkapp.tkw.tkw_routines import tk_focus_get, make_widget_ro, bind_children
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header

from pytkapp.pta_constants import CHILD_ACTIVE, CHILD_BUSY, CHILD_INACTIVE
from pytkapp.pta_constants import CHILD_WSTATE_NORMAL, CHILD_WSTATE_MAXIMIZED
from pytkapp.pta_constants import APP_UI_MODE_MDI, APP_UI_MODE_SDI, APP_UI_MODE_BAT
from pytkapp.pta_constants import CHILD_UI_MODE_MDI, CHILD_UI_MODE_SDI, CHILD_UI_MODE_CLI
from pytkapp.pta_constants import APP_RECENTLIST_LEN

###################################
## constants
###################################
gl_arrows = {}
if sys.platform == 'win32':
    gl_arrows['v']    = 'sb_v_double_arrow'
    gl_arrows['h']    = 'sb_h_double_arrow'
    gl_arrows['nwse'] = 'size_nw_se'
    gl_arrows['nesw'] = 'size_ne_sw'
else:
    gl_arrows['v']    = 'sb_v_double_arrow'
    gl_arrows['h']    = 'sb_h_double_arrow'
    gl_arrows['nwse'] = 'bottom_right_corner'
    gl_arrows['nesw'] = 'bottom_left_corner'

###################################
## globals
###################################
DEFAULT_BATCH_DELAY = 10

###################################
## classes
###################################
class BaseChild(Frame):
    """ base child class for application """

    def __init__( self, pw_container, po_app, **kw ):
        """ init child """

        # dont remove this attr !!!
        self.iamchild = 'X'

        self.__styledata = {}
        lo_superoptions = None
        if po_app is not None:
            lo_superoptions = po_app.get_options()

            self.__styledata['child.header.bg.active']   = novl(lo_superoptions.get_value('sys.child.header.bg.active'), 'dark blue')
            self.__styledata['child.header.fg.active']   = novl(lo_superoptions.get_value('sys.child.header.fg.active'), 'white')
            self.__styledata['child.header.bg.inactive'] = novl(lo_superoptions.get_value('sys.child.header.bg.inactive'), 'gray75')
            self.__styledata['child.header.fg.inactive'] = novl(lo_superoptions.get_value('sys.child.header.fg.inactive'), 'black')
            self.__styledata['child.hbutton.bg.active']   = novl(lo_superoptions.get_value('sys.child.hbutton.bg.active'), 'silver')
            self.__styledata['child.hbutton.bg.inactive'] = novl(lo_superoptions.get_value('sys.child.hbutton.bg.inactive'), 'gray20')
        else:
            self.__styledata['child.header.bg.active']   = 'dark blue'
            self.__styledata['child.header.fg.active']   = 'white'
            self.__styledata['child.header.bg.inactive'] = 'gray75'
            self.__styledata['child.header.fg.inactive'] = 'black'
            self.__styledata['child.hbutton.bg.active']   = 'silver'
            self.__styledata['child.hbutton.bg.inactive'] = 'gray20'

        parent_widget = kw.get('parentw', None)
        p_id = kw.get('childid', 'window')
        lv_title = kw.get('title', '')
        p_mw = kw.get('mw', 100)
        p_mh = kw.get('mh', 50)
        pv_icondata = kw.get('icon', pta_icons.get_icon('gv_child_header_icon'))

        self.__help = kw.get('helptext', [])
        self.__translator = kw.get('translator', None)
        self.__inittitle = lv_title

        Frame.__init__(self, pw_container, relief=RAISED, bd=1, takefocus=1)

        self.__id = p_id
        self.__container = pw_container

        # store operation assigned in BATCH mode (last in - first out)
        self.__batchlifo = []
        self.__batchbreak = threading.Event()
        self.__batchbreak.clear()
        self.__batchafid = None

        self.__th_unsafe = {}
        self.__th_safe = {}

        self.__ad_resources = {}
        self.__ad_subchildren = {}
        self.__nwtoplevels = []

        self.__al_xbinds = []

        self.__parentapp = po_app
        self.__parentwidget = parent_widget

        self.__state = CHILD_INACTIVE

        self.__uimode = kw.get('uimode', CHILD_UI_MODE_MDI)

        # with tk
        if self.__uimode != CHILD_UI_MODE_CLI:
            self.__titlevar = StringVar()

        if self.__uimode == CHILD_UI_MODE_MDI:
            # test arrows
            lw_tmpframe = Frame(self)
            for arr_item in gl_arrows:
                try:
                    lw_tmpframe.configure(cursor=gl_arrows[arr_item])
                except TclError:
                    lv_message = 'missed cursor: %s' % gl_arrows[arr_item]
                    xprint(lv_message)
                    gl_arrows[arr_item] = 'question_arrow'
            lw_tmpframe.destroy()

            ts = Frame(self, width=1, relief=RAISED, bd=1, cursor=gl_arrows['v'])
            ts.grid(row=0, column=0, columnspan=3, sticky=N+E+W+S)

            ls = Frame(self, width=1, relief=RAISED, bd=1, cursor=gl_arrows['h'])
            ls.grid(row=1, column=0, sticky=N+E+W+S)

            bs = Frame(self, width=1, relief=RAISED, bd=1, cursor=gl_arrows['v'])
            bs.grid(row=2, column=1, sticky=N+E+W+S)

            local_frame = Frame( self, relief=RAISED)

            lw_headerbar = Frame(local_frame, relief=RAISED, cursor="fleur", bg=self.get_styledata_key('child.header.bg.active'))
            self.__ad_resources['header_bar'] = lw_headerbar

            lw_headerbar.pack(side=TOP, fill=X)

            self.__titlevar.set(lv_title)
            img = PhotoImage(data=pv_icondata)
            titlelabel = Label(lw_headerbar, textvariable=self.__titlevar, fg=self.get_styledata_key('child.header.fg.active'), bg=self.get_styledata_key('child.header.bg.active'), compound=LEFT, image=img)
            titlelabel.pack(side=LEFT, fill=X)
            titlelabel.img = img
            self.__ad_resources['header_title_label'] = titlelabel
            self.__ad_resources['child_logo'] = img

            img = PhotoImage(data=pta_icons.get_icon('gv_child_header_help'))
            b = Button(lw_headerbar,
                       image=img,
                       command=self.show_help,
                       cursor="arrow",
                       width=12,
                       height=12,
                       activebackground=self.get_styledata_key('child.hbutton.bg.active'),
                       bg=self.get_styledata_key('child.hbutton.bg.inactive'))
            b.img = img
            b.pack(side=RIGHT, pady=1, padx=2)
            self.__ad_resources['header_help_btn'] = b
            b.pack_forget()

            img = PhotoImage(data=pta_icons.get_icon('gv_child_header_close'))
            b = Button(lw_headerbar,
                       image=img,
                       command=self.child_close,
                       cursor="arrow",
                       width=12,
                       height=12,
                       activebackground=self.get_styledata_key('child.hbutton.bg.active'),
                       bg=self.get_styledata_key('child.hbutton.bg.inactive'))
            b.img = img
            b.pack(side=RIGHT, pady=1, padx=2)
            self.__ad_resources['header_close_btn'] = b

            img = PhotoImage(data=pta_icons.get_icon('gv_child_header_maximize'))
            b = Button(lw_headerbar,
                       image=img,
                       command=self.call_geom_maximize,
                       cursor="arrow",
                       width=12,
                       height=12,
                       activebackground=self.get_styledata_key('child.hbutton.bg.active'),
                       bg=self.get_styledata_key('child.hbutton.bg.inactive') )
            b.img = img
            b.pack(side=RIGHT, pady=1)
            self.__ad_resources['header_wstate_btn'] = b

            self.child_reconf_help_btn()

            lw_workspace = Frame(local_frame, width=p_mw, height=p_mh, padx=2, pady=2, relief=SUNKEN, bd=2, takefocus=1)
        elif self.__uimode == CHILD_UI_MODE_SDI:
            lw_workspace = Frame(self, width=p_mw, height=p_mh, padx=2, pady=2, relief=RAISED, bd=2, takefocus=1)

        lw_workspace.pack(side=TOP, expand=YES, fill=BOTH)

        self.__workspace = lw_workspace

        if self.__uimode == CHILD_UI_MODE_MDI:
            local_frame.grid(row=1, column=1, sticky=N+E+W+S)

            rs = Frame(self, width=1, relief=RAISED, bd=1, cursor=gl_arrows['h'])
            rs.grid( row=1, column=2, sticky=N+E+W+S )

            sw = Frame(self, width=2, height=2, bg="gray30", relief=FLAT, bd=1, cursor=gl_arrows['nesw'])
            sw.grid( row=2, column=0, sticky=N+E+W+S )

            se = Frame(self, width=2, height=2, bg="gray30", relief=FLAT, bd=1, cursor=gl_arrows['nwse'])
            se.grid( row=2, column=2, sticky=N+E+W+S )

            self.rowconfigure( 1, weight=1 )
            self.columnconfigure( 1, weight=1 )

            # binding
            lw_headerbar.bind('<ButtonPress-1>', self.geom_checkup)
            titlelabel.bind('<ButtonPress-1>', self.geom_checkup)

            lw_headerbar.bind('<B1-Motion>', self.geom_moving_motion)
            titlelabel.bind('<B1-Motion>', self.geom_moving_motion)

            lw_headerbar.bind('<ButtonRelease-1>', self.geom_moving_release)
            titlelabel.bind('<ButtonRelease-1>', self.geom_moving_release)

            lw_headerbar.bind('<Double-Button-1>', self.geom_toggle)
            titlelabel.bind('<Double-Button-1>', self.geom_toggle)

            ts.bind('<ButtonPress-1>', self.geom_checkup)
            ls.bind('<ButtonPress-1>', self.geom_checkup)
            bs.bind('<ButtonPress-1>', self.geom_checkup)
            rs.bind('<ButtonPress-1>', self.geom_checkup)

            se.bind('<ButtonPress-1>', self.geom_checkup)
            sw.bind('<ButtonPress-1>', self.geom_checkup)

            # motion
            ts.bind('<B1-Motion>', self.geom_sizing_motion)
            ls.bind('<B1-Motion>', self.geom_sizing_motion)
            bs.bind('<B1-Motion>', self.geom_sizing_motion)
            rs.bind('<B1-Motion>', self.geom_sizing_motion)

            se.bind('<B1-Motion>', self.geom_sizing_motion)
            sw.bind('<B1-Motion>', self.geom_sizing_motion)

            # release
            ts.bind('<ButtonRelease-1>', self.geom_sizing_release)
            ls.bind('<ButtonRelease-1>', self.geom_sizing_release)
            bs.bind('<ButtonRelease-1>', self.geom_sizing_release)
            rs.bind('<ButtonRelease-1>', self.geom_sizing_release)

            se.bind('<ButtonRelease-1>', self.geom_sizing_release)
            sw.bind('<ButtonRelease-1>', self.geom_sizing_release)

            # keep anchors for child
            self.__anchor_ts = ts
            self.__anchor_ls = ls
            self.__anchor_bs = bs
            self.__anchor_rs = rs
            self.__anchor_se = se
            self.__anchor_sw = sw

        self.__wstate = CHILD_WSTATE_NORMAL

        self.__ad_geometry = {}
        self.__ad_geometry['up_x'] = None
        self.__ad_geometry['up_y'] = None
        self.__ad_geometry['min_w'] = p_mw
        self.__ad_geometry['min_h'] = p_mh
        self.__ad_geometry['old_x'] = 0
        self.__ad_geometry['old_y'] = 0
        self.__ad_geometry['old_w'] = p_mw
        self.__ad_geometry['old_h'] = p_mh

        # configure options >>>
        ll_optionsdata = kw.get('optionsdata', None)
        ll_rulesdata = kw.get('rulesdata', None)
        self.__options = None

        if ll_optionsdata is not None or lo_superoptions is not None:
            # need to determinate options UI mode
            if po_app.get_uimode() in (APP_UI_MODE_MDI, APP_UI_MODE_SDI, APP_UI_MODE_BAT):
                self.__options = OptionsContainer(OPTIONS_UI_MODE_TK, lo_superoptions)
            else:
                self.__options = OptionsContainer(OPTIONS_UI_MODE_NOTK, lo_superoptions)
            if ll_optionsdata is not None:
                try:
                    self.options_initconf(self.__options, ll_optionsdata, ll_rulesdata)
                except OptionError as x:
                    lv_outmessage = x.message
                    xprint(lv_outmessage)
                    sys.exit(2)

        # configure threads >>>
        lb_usethreads = False
        if po_app is not None:
            lb_usethreads = po_app.get_usethreads()
        self.__usethreads = lb_usethreads
        self.__thread = None
        self.__queue = queue.Queue()
        self.__stop_event = threading.Event()

        if self.__usethreads:
            self.otms_receiver()

        self.child_postinit()

        if self.__uimode == CHILD_UI_MODE_SDI:
            self.geom_maximize()

    def batchlifo_getdelay(self):
        """return delay between batch operations"""

        return novl(self.options_get_value('sys.batch.delay'), DEFAULT_BATCH_DELAY)

    def batchlifo_break(self):
        """set break flag"""

        self.__batchbreak.set()

    def batchlifo_isbreak(self):
        """return event"""

        return self.__batchbreak.is_set()

    def batchlifo_add(self, pf_oper, pv_thflag, pd_kw):
        """add oper and kw in lifo"""

        self.__batchlifo.append((pf_oper, pv_thflag, pd_kw,))

    def batchlifo_pop(self):
        """pop oper from lifo"""

        if self.__batchlifo:
            return self.__batchlifo.pop(0)
        else:
            return (None, None, None,)

    def batchlifo_process(self):
        """exec batch stack"""

        lb_lifo = self.batchlifo_check()

        # show initial notification
        if lb_lifo and not self.__batchafid:
            self.child_showinfo(_('Batch process started...'))

        if lb_lifo:
            if not self.__batchbreak.is_set():
                if not self.thread_inuse():
                    lf_oper, lv_thflag, ld_data = self.batchlifo_pop()

                    lv_len = self.batchlifo_len()

                    if lf_oper:
                        self.child_showinfo(_('executing batched operation "%s" with index [%s]...') % (lf_oper.__name__, lv_len,))

                        if ld_data:
                            lf_oper(**ld_data)
                        else:
                            lf_oper()
                    else:
                        self.child_showinfo(_('executing batched operation with index [%s]...') % (lv_len))

                self.__container.update_idletasks()
                self.__batchafid = self.__container.after(self.batchlifo_getdelay()*1000, self.batchlifo_process)
            else:
                # show final notification
                self.child_showwarning(_('Batch process breaked...'), silence=True)
        else:
            if self.thread_inuse():
                self.__container.update_idletasks()
                self.__batchafid = self.__container.after(self.batchlifo_getdelay()*1000, self.batchlifo_process)
            else:
                self.__batchafid = None

                # show final notification
                self.child_showinfo(_('Batch process ended...'))

                # mark batchbreak for parent checks
                self.__batchbreak.set()

    def batchlifo_len(self):
        """get length"""

        return len(self.__batchlifo)

    def batchlifo_check(self):
        """check lifo"""

        if self.__batchlifo:
            return True
        else:
            return False

    def get_styledata_key(self, pv_key, pv_def=None):
        """ get value from styledata """

        return self.__styledata.get(pv_key, pv_def)

    def child_add_nowaittoplevel(self, pw_toplevel):
        """ add 'indendendent' toplevel """

        self.__nwtoplevels.append(pw_toplevel)

    def child_close_nwtoplevels(self):
        """ close all known nw-toplevels """

        for nw_top in self.__nwtoplevels[:]:
            try:
                nw_top.destroy()
            except Others:
                lv_message = get_estr()
                print(lv_message)

        self.__nwtoplevels = []

    def child_postinit(self):
        """ post init routines """

        raise NotImplementedError

    def get_usethreads(self):
        """ return usethreads state of child """

        return self.__usethreads

    def thread_inuse(self):
        """ check thread """

        return self.__thread is not None

    def otms_logger(self, pd_message):
        """ over-thread message system - logger
            put message in queue or process it immediate
        """

        pd_message.setdefault('at', True)

        if self.__usethreads:
            self.__queue.put( pd_message )
        else:
            self.otms_processor( pd_message )

    def otms_stopper(self):
        """ over-thread message system - stop routines"""

        try:
            while not self.__queue.empty():
                ld_message = self.__queue.get()
                self.otms_processor(ld_message)
                self.__container.update_idletasks()
        except queue.Empty:
            pass

    def otms_receiver(self, pv_atonce=20, pb_restart=True):
        """ over-thread message system - receiver
            extract message from queue and re-run itself
        """

        if self.__queue:
            try:
                lv_counter = 0
                while not self.__queue.empty() and lv_counter < pv_atonce:
                    ld_message = self.__queue.get()
                    self.otms_processor(ld_message)
                    self.__container.update_idletasks()
                    lv_counter += 1
            except queue.Empty:
                pass

            if pb_restart:
                self.set_resource_item('receiver_afid', self.__container.after(100, self.otms_receiver))
            else:
                self.set_resource_item('receiver_afid', None)

    def child_logging(self, pv_message, pb_at=True, pb_see=True, pb_forced=False):
        """child internal logging in optional resource "log" """

        lw_log = self.get_resource_item('log')
        lw_parent = self.get_parentwidget()

        if not lw_log and lw_parent:
            lw_parent.child_logging(pv_message, pb_at, pb_see, pb_forced)
        else:
            if pb_at:
                lv_message = '%s %s\n' % (get_logtime(), pv_message.rstrip())
            else:
                lv_message = '%s\n' % (pv_message.rstrip())

            if lw_log is not None:
                try:
                    lw_log.insert_data(lv_message, see_=pb_see)
                except Others:
                    xprint(lv_message)
            elif not pb_forced:
                xprint(lv_message)

    def otms_processor_customend(self, pv_thname='', pv_data=None):
        """ over-thread message system - processor
            user-defined routines after process stopping
        """

        pass

    def otms_processor( self, pd_message ):
        """ over-thread message system - processor
            process message
        """

        try:
            lv_type = pd_message['type']
            lv_data = pd_message['data']

            lb_at = pd_message.get('at', True)

            if lv_type == 'LOG':
                self.child_logging(lv_data, lb_at, True)
            elif lv_type == 'PROCESS_END':
                # store thread name
                try:
                    lv_thname = self.get_thread().getName()
                except Others:
                    lv_thname = None

                # remove thread and unblock interface
                self.thread_stop()

                # call custom end routines
                self.otms_processor_customend(lv_thname, lv_data)

            elif lv_type in ('INFO', 'WARNING', 'ERROR'):
                lv_detail = pd_message.get('detail', None)
                if lv_type == 'INFO':
                    self.child_showinfo(lv_data, detail=lv_detail)
                elif lv_type == 'WARNING':
                    self.child_showwarning(lv_data, detail=lv_detail)
                elif lv_type == 'ERROR':
                    self.child_showerror(lv_data, detail=lv_detail)

            if not self.get_usethreads():
                self.__container.update_idletasks()
        except Others:
            lv_message = 'failed to process thread message: %s' % get_estr()
            xprint(lv_message)

    def child_reconf_help_btn( self ):
        """ hide or create help btn """

        lw_helpbtn = self.__ad_resources.get('header_help_btn', None)

        if self.__help:
            lw_helpbtn.pack(side=RIGHT, pady=1, padx=2)
        else:
            lw_helpbtn.pack_forget()

    def get_rthitem(self, pv_name, pv_def=None):
        """ get item from res. or th-lists"""

        if pv_name in self.__ad_resources:
            return self.__ad_resources[pv_name]
        elif pv_name in self.__th_safe:
            return self.__th_safe[pv_name]
        elif pv_name in self.__th_unsafe:
            return self.__th_unsafe[pv_name]
        else:
            return pv_def

    def get_resource_item( self, pv_name ):
        """ get some ctrl item """

        return self.__ad_resources.get( pv_name, None )

    def set_resource_item( self, pv_name, pv_value ):
        """ set some ctrl item """

        self.__ad_resources[ pv_name ] = pv_value

    def options_initconf(self, po_options, pl_options, pl_rules):
        """ fill options and rules """

        # options itself >>>
        for optiondata in pl_options:
            po_options.register_option( optiondata['name'],
                                        optiondata['type'],
                                        optiondata['default'],
                                        reset=optiondata.get('reset',1),
                                        export=optiondata.get('export',0),
                                        desc=optiondata.get('desc','???'),
                                        wstyle=optiondata.get('wstyle',None),
                                        minv=optiondata.get('min',0),
                                        maxv=optiondata.get('max',1),
                                        stepv=optiondata.get('step',None),
                                        cdata=optiondata.get('cdata',None),
                                        group=optiondata.get('group',None)
                                      )

        # rules - if exists >>>
        if pl_rules is not None:
            for ruledata in pl_rules:
                po_options.register_rule( *ruledata )

        # reset options >>>
        po_options.reset(force=1)

        self.options_postconf(po_options)

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """

        raise NotImplementedError

    def show_help( self ):
        """ show help text """

        if self.__help.startswith('@'):
            # help was defined as external file
            try:
                lv_helpfile = self.__help[1:]
                open_file(lv_helpfile)
            except Others:
                lv_detail = get_estr()
                lv_message = 'Error on load: %s' % self.__help
                self.child_showerror(lv_message, detail=lv_detail)
        else:
            # help was defined as list
            if self.__state == CHILD_ACTIVE:
                lv_wasactive = True
                self.child_deactivate()
            else:
                lv_wasactive = False

            top_page = Toplevel(self.__container)
            top_page.withdraw()

            top_page.title(_('Help'))
            top_page.protocol("WM_DELETE_WINDOW", top_page.destroy)

            top_page.transient( self.__container )
            top_page.columnconfigure( 0, weight=1 )

            top_frame = Frame(top_page)
            top_frame.grid(sticky=N+E+W+S)

            text = scrolledtext.ScrolledText( top_frame, bg="white", width=80, height=15, padx=2, pady=2 )
            text.pack(side=TOP, fill=BOTH, expand=YES)

            if self.__translator is not None:
                text.insert(END, '\n'.join([self.__translator.get(s) for s in self.__help]))
            else:
                text.insert(END, '\n'.join([s for s in self.__help]))
            make_widget_ro( text )

            top_page.update_idletasks()
            ws_x = self.winfo_rootx()+50
            ws_y = self.winfo_rooty()+50

            lv_width  = top_page.winfo_reqwidth()
            lv_height = top_page.winfo_reqheight()

            top_page.geometry(str(lv_width)+"x"+str(lv_height)+"+"+str(ws_x)+"+"+str(ws_y))
            top_page.resizable( width = False, height = False )

            top_page.minsize(lv_width, lv_height)

            top_page.deiconify()
            top_page.lift()
            top_page.focus_set()
            top_page.grab_set()

            self.__container.wait_window( top_page )

            if lv_wasactive:
                self.child_activate()

    def child_reconf_close_btn( self, pf_command ):
        """ recommand close btn """

        self.__ad_resources['header_close_btn'].configure(command = pf_command)

    def get_workspace( self ):
        """ get child own workspace """

        return self.__workspace

    def subchild_generate_id( self, pv_id ):
        """ generate id for subchild """

        return self.__id + ':' + pv_id

    def get_inittitle(self):
        """ return initial title """

        return self.__inittitle

    def get_classname(self):
        """get class name"""

        return str(self.__class__).split('.')[-1]

    def get_recentlen(self):
        """get len of recent list specifief for console or app"""

        lv_classname = self.get_classname().lower()
        lv_recentlen = self.options_get_value('%s:recentlen' % lv_classname)

        if not lv_recentlen:
            lv_recentlen = self.options_get_value('sys_recentlen')

        return novl(lv_recentlen, APP_RECENTLIST_LEN)

    def process_recentdata(self, somedata):
        """add data in recent list"""

        lv_classname = self.get_classname().lower()

        # get without copy !
        ll_recentlist = self.options_get_value('%s:recentlist' % lv_classname, False, False)

        if ll_recentlist is not None:
            lv_recentlen = self.get_recentlen()

            # check data in list
            try:
                ll_recentlist.pop(ll_recentlist.index(somedata))
            except ValueError:
                pass

            ll_recentlist.insert(0, somedata)

            # strip recent list
            ll_recentlist = ll_recentlist[:lv_recentlen]

            self.options_set_value('%s:recentlist' % lv_classname, ll_recentlist, pb_superset=True)

    def app_add_recentrep(self, pv_reppath):
        """add rrep in app list"""

        lo_app = self.get_parentapp()
        if lo_app:
            lo_app.app_add_recentrep(pv_reppath)

    def subchild_allowed(self):
        """ request subchild from parent """

        return self.__parentapp.app_subchild_allowed(self, len(self.get_subchildren_ids()))

    def call_subchild_add(self, pv_id, pv_name, class_=None):
        """ add subchild """

        if not self.subchild_exist(pv_id):
            if class_ is None:
                self.child_showwarning(_('Sub-child class is missed !'))
            elif not issubclass(class_, BaseChild):
                self.child_showwarning(_('Sub-child class must subclassed from BaseChild !'))
            elif self.__uimode == CHILD_UI_MODE_SDI:
                self.child_showwarning(_('Sub-children not allowed in this UI mode !'))
            else:
                if self.subchild_allowed():
                    self.subchild_generate(pv_id, pv_name, class_)
                else:
                    self.child_showwarning(_('Maximum number of sub-children !'))
        else:
            self.subchild_focus_set(pv_id)

    def subchild_generate(self, pv_id, pv_name, class_=None):
        """ add subchild """

        self.subchild_add(pv_id, pv_name, class_)
        self.subchild_wrap(pv_id)
        self.subchild_focus_set(pv_id)

    def subchild_exist( self, pv_id ):
        """ check whether exists subchild with specified id """

        lv_subchildid = self.subchild_generate_id( pv_id )

        return lv_subchildid in self.__ad_subchildren

    def subchild_add( self, pv_id, pv_name, class_ ):
        """ initialize subchild """

        lv_subchildid = self.subchild_generate_id( pv_id )

        lo_child = self.__parentapp.app_subchild_add( lv_subchildid, pv_name, self, class_ )
        self.__ad_subchildren[ lv_subchildid ] = lo_child

        return lo_child

    def subchild_wrap( self, pv_id ):
        """ place and bind subchild """

        lv_subchildid = self.subchild_generate_id( pv_id )
        lo_child = self.__ad_subchildren[ lv_subchildid ]

        lo_child.geom_propagate()
        self.__parentapp.app_focus2child_bind(lo_child, lv_subchildid)

        lv_x = self.winfo_x()
        lv_y = self.winfo_y()
        lo_child.place(x=lv_x+50, y=lv_y+50)

    def subchild_focus_set( self, pv_id ):
        """ show subchild througout application """

        lv_subchildid = self.subchild_generate_id( pv_id )

        self.__parentapp.app_focus2child_set(lv_subchildid, 'show_sub')

    def get_subchildren_ids( self ):
        """ get list of sub-children identifiers """

        return list( self.__ad_subchildren.keys() )

    def subchild_close( self, pv_subchildid ):
        """ close subchild """

        lo_subchild = self.__ad_subchildren[ pv_subchildid ]

        lo_subchild.child_close()
        del self.__ad_subchildren[ pv_subchildid ]

    def child_preclose(self):
        """ preclose routines """

        pass

    def child_close( self ):
        """ close child itself and it sub-children """

        if self.__batchafid:
            self.__container.after_cancel(self.__batchafid)
        self.__batchbreak.set()

        self.child_preclose()

        self.child_close_nwtoplevels()

        ll_children = self.__ad_subchildren.keys()
        for child in ll_children:
            if hasattr(self.__ad_subchildren[child], 'child_close'):
                self.__ad_subchildren[child].child_close()

            del self.__ad_subchildren[child]

        # clear content
        lw_clbtn = self.__ad_resources.get('header_close_btn', None)
        if lw_clbtn:
            lw_clbtn.configure(command=None)
            lw_clbtn.destroy()
        del lw_clbtn

        if self.__usethreads:
            self.otms_stopper()

        self.__th_unsafe = {}
        self.__th_safe = {}

        self.__ad_resources = {}
        self.__ad_subchildren = {}
        self.__nwtoplevels = []

        self.__al_xbinds = []

        self.__usethreads = None
        self.__thread     = None
        self.__queue      = None
        self.__stop_event = None

        # forget parent
        self.__parentapp    = None
        self.__parentwidget = None
        self.__options      = None
        self.__workspace    = None
        self.__container    = None

        self.destroy()

    def geom_toggle(self, event):
        """ toggle state of child window """

        if self.__wstate == CHILD_WSTATE_NORMAL:
            self.__ad_geometry['toggle_x'] = self.winfo_x()
            self.__ad_geometry['toggle_y'] = self.winfo_y()
            self.call_geom_maximize()
        else:
            self.call_geom_restore()

        return "break"

    def get_thread(self):
        """ get thread """

        return self.__thread

    def get_queue(self):
        """ get queue """

        return self.__queue

    def get_stop_event(self):
        """ get stop event """

        return self.__stop_event

    def process_start(self, pv_name, pf_subprogram):
        """ start thread process """

        self.thread_start(pv_name, pf_subprogram)

    def process_stop(self):
        """ stop thread process """

        if not self.__stop_event.is_set():
            self.__stop_event.set()

        if self.__thread is not None:
            if self.__usethreads and self.__thread.isAlive():
                self.__thread.join()

            while not self.__queue.empty():
                if self.get_resource_item('receiver_afid') is not None:
                    self.__container.after_cancel(self.get_resource_item('receiver_afid'))
                self.otms_receiver(999)

    def thread_set_item(self, pv_itemname, po_itemvalue, pv_group='unsafe'):
        """ set thread-related item """

        if pv_group == 'unsafe':
            self.__th_unsafe[pv_itemname] = po_itemvalue
        elif pv_group == 'safe':
            self.__th_safe[pv_itemname] = po_itemvalue
        else:
            lv_message = _('unknown group "%s" for thread-related item') % pv_group
            print(lv_message)

    def thread_set_safe_item(self, pv_itemname, po_itemvalue):
        """ set thread unsafe item """

        self.thread_set_item(pv_itemname, po_itemvalue, 'safe')

    def thread_set_unsafe_item(self, pv_itemname, po_itemvalue):
        """ set thread unsafe item """

        self.thread_set_item(pv_itemname, po_itemvalue, 'unsafe')

    def thread_get_item(self, pv_itemname, pv_group='unsafe'):
        """ get thread-related item """

        lv_out = None
        ld_dict = None

        if pv_group == 'unsafe':
            ld_dict = self.__th_unsafe
        elif pv_group == 'safe':
            ld_dict = self.__th_safe
        else:
            lv_message = _('unknown group "%s" for thread-related item') % pv_group
            print(lv_message)

        if ld_dict is not None:
            lv_out = ld_dict.get(pv_itemname, None)

        return lv_out

    def thread_get_safe_item(self, pv_itemname):
        """ get thread unsafe item """

        return self.thread_get_item(pv_itemname, 'safe')

    def thread_get_unsafe_item(self, pv_itemname):
        """ get thread unsafe item """

        return self.thread_get_item(pv_itemname, 'unsafe')

    def thread_items_process(self, pv_group='unsafe', pv_process='block'):
        """ process on some thread-related items """

        if pv_group == 'unsafe':
            ld_dict = self.__th_unsafe
        elif pv_group == 'safe':
            ld_dict = self.__th_safe
        else:
            lv_message = _('unknown group "%s" for thread-related items') % pv_group
            print(lv_message)
            ld_dict = None

        if ld_dict is not None:
            for key, value in ld_dict.items():
                try:
                    custom_method = getattr(self, 'th_unsafe_item_%s_%s' % (key, pv_process), None)
                    if custom_method is not None:
                        custom_method(key, value)
                    elif issubclass(value.__class__, Widget):
                        if pv_process == 'block':
                            value.configure(state=DISABLED)
                        elif pv_process == 'unblock':
                            value.configure(state=NORMAL)
                        else:
                            lv_message = _('unknown process "%s" for thread-related items') % pv_process
                            print(lv_message)

                except Others:
                    lv_message = 'try to %s th-unsafe item "%s": %s' % (pv_process, key, get_estr())
                    print(lv_message)

    def thread_items_block_safe(self):
        """ block thread-safe items """

        self.thread_items_process('safe', 'block')

    def thread_items_block_unsafe(self):
        """ block thread-unsafe items """

        self.thread_items_process('unsafe', 'block')

    def thread_items_unblock_safe(self):
        """ unblock thread-safe items """

        self.thread_items_process('safe', 'unblock')

    def thread_items_unblock_unsafe(self):
        """ unblock thread-unsafe items """

        self.thread_items_process('unsafe', 'unblock')

    def thread_start(self, process_name, process_body):
        """ start thread in child """

        if self.__thread is None or not self.__thread.isAlive():
            if self.__usethreads:
                self.__thread = threading.Thread(None,
                                                 target=process_body,
                                                 name=process_name
                                                 )
            else:
                self.__thread = DummyThread(None,
                                            target=process_body,
                                            name=process_name
                                            )

            self.__stop_event.clear()
            self.thread_items_block_unsafe()
            self.thread_items_unblock_safe()
            self.family_gui_reconf()

            self.__thread.start()
        else:
            self.child_showwarning(_('Failed to start thread'))

    def thread_stop(self):
        """ stop thread in child """

        self.__thread = None
        self.thread_items_unblock_unsafe()
        self.thread_items_block_safe()
        self.family_gui_reconf()

    def family_gui_reconf(self):
        """ reconf child and app controls """

        self.child_gui_reconf()
        self.__parentapp.app_gui_reconf()

    def child_gui_reconf(self):
        """ reconf child gui controls """

        raise NotImplementedError

    def child_gui_init(self):
        """ create widgets for child """

        self.child_create_widgets()

        self.child_gui_postinit()

    def child_gui_postinit(self):
        """ post-init routines for gui """

        raise NotImplementedError

    def child_create_widgets(self):
        """ fill child workspace """

        raise NotImplementedError

    def geom_propagate(self):
        """ save child dimensions and propagate it """

        self.geom_measure()
        self.configure( width=self.__ad_geometry['min_w'], height=self.__ad_geometry['min_h'] )
        self.update_idletasks()
        self.grid_propagate(0)

    def xbind_add(self, event, command):
        """ bind children and store command for future re-bind """

        bind_children( self, event, command )

        self.__al_xbinds.append( ( event, command ) )

    def xbind_get(self, pv_index=None):
        """ return xbind or copy of all """

        if pv_index is None:
            return self.__al_xbinds[:]
        else:
            return self.__al_xbinds[pv_index]

    def xbind_reapply(self, pv_index=None):
        """ re-apply xbinds to child """

        if pv_index is None:
            for xbind_data in self.__al_xbinds:
                bind_children( self, xbind_data[0], xbind_data[1] )
        else:
            xbind_data = self.__al_xbinds[pv_index]
            bind_children( self, xbind_data[0], xbind_data[1] )

    def child_activate(self, p_prev=None):
        """ activate child """

        if self.__state != CHILD_BUSY:
            try:
                if self.__state != CHILD_ACTIVE:

                    self.__state = CHILD_BUSY

                    if p_prev is None:
                        self.lift()
                    else:
                        self.lift( p_prev )

                    if self.__uimode == CHILD_UI_MODE_MDI:
                        self.__ad_resources['header_bar'].configure( bg=self.get_styledata_key('child.header.bg.active') )
                        self.__ad_resources['header_title_label'].configure( bg=self.get_styledata_key('child.header.bg.active'),
                                                                             fg=self.get_styledata_key('child.header.fg.active') )

                    # change focus to activated child
                    self.focus_set()
                    self.update_idletasks()

                    self.__state = CHILD_ACTIVE
            except Others:
                lv_message = 'failed to activate child: %s' % (get_estr())
                xprint(lv_message)

    def child_deactivate(self, p_next=None):
        """ deactivate child """

        if self.__state != CHILD_BUSY:
            try:
                if self.__state != CHILD_INACTIVE:

                    self.__state = CHILD_BUSY

                    if p_next is not None:
                        self.lower( p_next )

                    if self.__uimode == CHILD_UI_MODE_MDI:
                        self.__ad_resources['header_bar'].configure( bg=self.get_styledata_key('child.header.bg.inactive') )
                        self.__ad_resources['header_title_label'].configure( bg=self.get_styledata_key('child.header.bg.inactive'),
                                                                             fg=self.get_styledata_key('child.header.fg.inactive') )

                    # release child
                    try:
                        lw_tp = self.winfo_toplevel()
                        lw_f = tk_focus_get( lw_tp )
                        if lw_f is not None:
                            lw_f.grab_release()
                    except Others:
                        lv_message = 'failed to release child: %s' % (get_estr())
                        xprint( lv_message )
                    self.update_idletasks()

                    self.__state = CHILD_INACTIVE
            except Others:
                lv_message = 'failed to deactivate child: %s' % (get_estr())
                xprint(lv_message)

    def geom_checkup(self, event):
        """ save child geometry ( coords ) """

        if self.__wstate == CHILD_WSTATE_NORMAL:
            self.__ad_geometry['up_x'] = self.winfo_pointerx()
            self.__ad_geometry['up_y'] = self.winfo_pointery()

            self.__ad_geometry['old_x'] = self.winfo_x()
            self.__ad_geometry['old_y'] = self.winfo_y()

            self.__ad_geometry['old_w'] = self.winfo_width()
            self.__ad_geometry['old_h'] = self.winfo_height()

    def get_id(self):
        """ return child id """

        return self.__id

    def get_state( self ):
        """ get state of child """

        return self.__state

    def get_wstate( self ):
        """ get state of child window """

        return self.__wstate

    def get_description(self):
        """ return tuple (sb1,sb2,sb3) for app statusbar """

        lv_sb1 = ''
        lv_sb2 = ''
        lv_sb3 = ''

        lv_sb1 = '%s' % self.get_title()
        lv_sb2 = '%s' % self.get_state()
        ll_children = self.get_subchildren_ids()
        if len(ll_children) == 0:
            lv_sb3 = 'w/o children'
        else:
            lv_sb3 = 'children: %s' % (', '.join(ll_children))

        return (lv_sb1, lv_sb2, lv_sb3)

    def get_title(self):
        """ return child title """

        return self.__titlevar.get()

    def set_title(self, lv_title):
        """ change child title """

        self.__titlevar.set(lv_title)
        lo_parentapp = self.get_parentapp()
        if lo_parentapp:
            if lo_parentapp.get_uimode() != APP_UI_MODE_BAT:
                lo_parentapp.wmenu_configure_item(self.get_id(), 'rename', label=lv_title)
            else:
                lo_parentapp.app_reconf_chlog_combo()

    def geom_sizing_motion(self, event):
        """ calc new size and draw moveable counter for child """

        try:
            if self.__wstate == CHILD_WSTATE_NORMAL:

                # determ. direction
                if event.widget == self.__anchor_ls:
                    move_h = True
                    move_v = False
                    size_h = True
                    size_v = False
                elif event.widget == self.__anchor_rs:
                    move_h = False
                    move_v = False
                    size_h = True
                    size_v = False
                elif event.widget == self.__anchor_ts:
                    move_h = False
                    move_v = True
                    size_h = False
                    size_v = True
                elif event.widget == self.__anchor_bs:
                    move_h = False
                    move_v = False
                    size_h = False
                    size_v = True
                elif event.widget == self.__anchor_se:
                    move_h = False
                    move_v = False
                    size_h = True
                    size_v = True
                elif event.widget == self.__anchor_sw:
                    move_h = True
                    move_v = False
                    size_h = True
                    size_v = True
                else:
                    return

                lv_swpx = self.winfo_pointerx()
                lv_swpy = self.winfo_pointery()

                sx = lv_swpx - novl(self.__ad_geometry['up_x'], lv_swpx)
                sy = lv_swpy - novl(self.__ad_geometry['up_y'], lv_swpy)

                sww = self.winfo_width()
                swh = self.winfo_height()

                smh = self.__container.winfo_height()
                smw = self.__container.winfo_width()

                # check bottom-right corner
                lv_maxx = self.__container.winfo_rootx() + smw - 1
                lv_maxy = self.__container.winfo_rooty() + smh - 1

                if move_h:
                    sx *= -1
                if move_v:
                    sy *= -1

                ##################################################
                ## calc horizontal shift
                ##################################################
                x0 = self.__ad_geometry['old_x']
                # left border
                if event.widget in [self.__anchor_ls, self.__anchor_sw] and event.x_root <= self.__container.winfo_rootx()+1:
                    sx = self.__ad_geometry['old_x']
                # right border
                elif event.widget in [self.__anchor_rs, self.__anchor_se] and event.x_root >= lv_maxx:
                    sx = lv_maxx-self.winfo_rootx()-self.__ad_geometry['old_w']
                # minsize
                elif self.__ad_geometry['old_w'] + sx <= self.__ad_geometry['min_w']:
                    sx = self.__ad_geometry['min_w']-self.__ad_geometry['old_w']
                # check back-sizing
                if event.widget == self.__anchor_ls:
                    if self.winfo_pointerx() >= self.__ad_geometry['up_x'] + self.__ad_geometry['old_w'] - self.__ad_geometry['min_w']:
                        move_h = False
                    x0 += -sx
                elif event.widget == self.__anchor_sw:
                    if self.winfo_pointerx() >= self.__ad_geometry['up_x'] + self.__ad_geometry['old_w'] - self.__ad_geometry['min_w']:
                        move_h = False
                    x0 += -sx

                ##################################################
                ## calc vertical shift
                ##################################################
                y0 = self.__ad_geometry['old_y']
                # top border
                if event.widget in [self.__anchor_ts] and event.y_root <= self.__container.winfo_rooty()+1:
                    sy = self.__ad_geometry['old_y']
                # bottom border
                elif event.widget in [self.__anchor_bs, self.__anchor_se, self.__anchor_sw] and event.y_root >= lv_maxy:
                    sy = lv_maxy-self.winfo_rooty()-self.__ad_geometry['old_h']
                # minsize
                elif self.__ad_geometry['old_h'] + sy <= self.__ad_geometry['min_h']:
                    sy = self.__ad_geometry['min_h'] - self.__ad_geometry['old_h']

                if event.widget == self.__anchor_ts:
                    # check back-sizing
                    if self.winfo_pointery() >= self.__ad_geometry['up_y'] + self.__ad_geometry['old_h'] - self.__ad_geometry['min_h']:
                        move_v = False
                    y0 += -sy

                self.get_parentapp().app_workspace_hide_mc()

                ##################################################
                ## countering
                ##################################################
                if not size_h and not move_h:
                    sx = 0
                elif not size_v and not move_v:
                    sy = 0

                if size_h and not size_v:
                    self.get_parentapp().app_workspace_draw_mc(x0, y0, x0+sww+sx, y0+swh)
                if size_v and not size_h:
                    self.get_parentapp().app_workspace_draw_mc(x0, y0, x0+sww, y0+swh+sy)
                if size_v and size_h:
                    self.get_parentapp().app_workspace_draw_mc(x0, y0, x0+sww+sx, y0+swh+sy)

        except Others:
            lv_message = 'geom_sizing_motion: %s' % (get_estr())
            xprint(lv_message)
        finally:
            self.update_idletasks()

    def geom_sizing_release(self, event):
        """ change child size and place on new position on B1-release """

        try:
            if self.__wstate == CHILD_WSTATE_NORMAL:

                # determ. direction
                if event.widget == self.__anchor_ls:
                    move_h = True
                    move_v = False
                    size_h = True
                    size_v = False
                elif event.widget == self.__anchor_rs:
                    move_h = False
                    move_v = False
                    size_h = True
                    size_v = False
                elif event.widget == self.__anchor_ts:
                    move_h = False
                    move_v = True
                    size_h = False
                    size_v = True
                elif event.widget == self.__anchor_bs:
                    move_h = False
                    move_v = False
                    size_h = False
                    size_v = True
                elif event.widget == self.__anchor_se:
                    move_h = False
                    move_v = False
                    size_h = True
                    size_v = True
                elif event.widget == self.__anchor_sw:
                    move_h = True
                    move_v = False
                    size_h = True
                    size_v = True
                else:
                    return

                lv_swpx = self.winfo_pointerx()
                lv_swpy = self.winfo_pointery()

                sx = lv_swpx - novl(self.__ad_geometry['up_x'], lv_swpx)
                sy = lv_swpy - novl(self.__ad_geometry['up_y'], lv_swpy)

                sww = self.winfo_width()
                swh = self.winfo_height()

                smh = self.__container.winfo_height()
                smw = self.__container.winfo_width()

                # check bottom-right corner
                lv_maxx = self.__container.winfo_rootx() + smw - 1
                lv_maxy = self.__container.winfo_rooty() + smh - 1

                if move_h:
                    sx *= -1
                if move_v:
                    sy *= -1

                ##################################################
                ## calc horizontal shift
                ##################################################
                x0 = self.__ad_geometry['old_x']
                # left border
                if event.widget in [self.__anchor_ls, self.__anchor_sw] and event.x_root <= self.__container.winfo_rootx()+1:
                    sx = self.__ad_geometry['old_x']
                # right border
                elif event.widget in [self.__anchor_rs, self.__anchor_se] and event.x_root >= lv_maxx:
                    sx = lv_maxx-self.winfo_rootx()-self.__ad_geometry['old_w']
                # minsize
                elif self.__ad_geometry['old_w'] + sx <= self.__ad_geometry['min_w']:
                    sx = self.__ad_geometry['min_w']-self.__ad_geometry['old_w']
                # check back-sizing
                if event.widget == self.__anchor_ls:
                    if self.winfo_pointerx() >= self.__ad_geometry['up_x'] + self.__ad_geometry['old_w'] - self.__ad_geometry['min_w']:
                        move_h = False
                    x0 += -sx
                elif event.widget == self.__anchor_sw:
                    if self.winfo_pointerx() >= self.__ad_geometry['up_x'] + self.__ad_geometry['old_w'] - self.__ad_geometry['min_w']:
                        move_h = False
                    x0 += -sx

                ##################################################
                ## calc vertical shift
                ##################################################
                y0 = self.__ad_geometry['old_y']
                # top border
                if event.widget in [self.__anchor_ts] and event.y_root <= self.__container.winfo_rooty()+1:
                    sy = self.__ad_geometry['old_y']
                # bottom border
                elif event.widget in [self.__anchor_bs, self.__anchor_se, self.__anchor_sw] and event.y_root >= lv_maxy:
                    sy = lv_maxy-self.winfo_rooty()-self.__ad_geometry['old_h']
                # minsize
                elif self.__ad_geometry['old_h'] + sy <= self.__ad_geometry['min_h']:
                    sy = self.__ad_geometry['min_h'] - self.__ad_geometry['old_h']

                if event.widget == self.__anchor_ts:
                    # check back-sizing
                    if self.winfo_pointery() >= self.__ad_geometry['up_y'] + self.__ad_geometry['old_h'] - self.__ad_geometry['min_h']:
                        move_v = False
                    y0 += -sy

                ##################################################
                ## sizing
                ##################################################
                if not size_h and not move_h:
                    sx = 0
                elif not size_v and not move_v:
                    sy = 0

                if size_h and not size_v:
                    self.configure( width=self.__ad_geometry['old_w']+sx)
                if size_v and not size_h:
                    self.configure( height=self.__ad_geometry['old_h']+sy )
                if size_v and size_h:
                    self.configure( width=self.__ad_geometry['old_w']+sx, height=self.__ad_geometry['old_h']+sy )

                ##################################################
                ## draw
                ##################################################
                self.get_parentapp().app_workspace_hide_mc()
                self.place( x=x0, y=y0 )

        except Others:
            lv_message = 'geom_sizing_release: %s' % (get_estr())
            xprint(lv_message)
        finally:
            self.update_idletasks()

    def geom_moving_release(self, event, p_moveh=True, p_movev=True):
        """ place child on B1 release """

        try:
            if self.__wstate == CHILD_WSTATE_NORMAL:

                sx = self.winfo_pointerx() - novl(self.__ad_geometry['up_x'], self.winfo_pointerx())
                sy = self.winfo_pointery() - novl(self.__ad_geometry['up_y'], self.winfo_pointery())

                if p_moveh:
                    vx = self.__ad_geometry['old_x'] + sx
                else:
                    vx = self.__ad_geometry['old_x']
                if p_movev:
                    vy = self.__ad_geometry['old_y'] + sy
                else:
                    vy = self.__ad_geometry['old_y']

                # fixme: remove geom limitation on moving (except TOP)

                ## check top-left corner
                #if event.x_root < self.__container.winfo_rootx()+1 or vx <= 0:
                    #vx = 1
                if event.y_root < self.__container.winfo_rooty()+1 or vy <= 0:
                    vy = 1

                #sww = self.winfo_width()
                #smw = self.__container.winfo_width()

                #swh = self.winfo_height()
                #smh = self.__container.winfo_height()

                ## check bottom-right corner
                #lv_maxx = self.__container.winfo_rootx()+smw-1
                #lv_maxy = self.__container.winfo_rooty()+smh-1

                #if event.x_root > lv_maxx or vx+sww >= smw:
                    #vx = smw-sww-1

                #if event.y_root > lv_maxy or vy+swh >= smh:
                    #vy = smh-swh-1

                if not p_moveh:
                    vx = self.winfo_x()
                if not p_movev:
                    vy = self.winfo_y()

                ##################################################
                ## draw
                ##################################################
                self.get_parentapp().app_workspace_hide_mc()
                self.place( x=vx, y=vy )
        except Others:
            lv_message = 'geom_moving_release: %s' % (get_estr())
            xprint(lv_message)
        finally:
            self.update_idletasks()

    def geom_moving_motion(self, event, p_moveh=True, p_movev=True):
        """ process child moving """

        try:
            if self.__wstate == CHILD_WSTATE_NORMAL:

                sx = self.winfo_pointerx() - novl(self.__ad_geometry['up_x'], self.winfo_pointerx())
                sy = self.winfo_pointery() - novl(self.__ad_geometry['up_y'], self.winfo_pointery())

                if p_moveh:
                    vx = self.__ad_geometry['old_x'] + sx
                else:
                    vx = self.__ad_geometry['old_x']
                if p_movev:
                    vy = self.__ad_geometry['old_y'] + sy
                else:
                    vy = self.__ad_geometry['old_y']

                # fixme: remove geom limitation on moving (except TOP)

                ## check top-left corner
                #if event.x_root < self.__container.winfo_rootx()+1 or vx <= 0:
                    #vx = 1
                if event.y_root < self.__container.winfo_rooty()+1 or vy <= 0:
                    vy = 1

                sww = self.winfo_width()
                #smw = self.__container.winfo_width()

                swh = self.winfo_height()
                #smh = self.__container.winfo_height()

                ## check bottom-right corner
                #lv_maxx = self.__container.winfo_rootx()+smw-1
                #lv_maxy = self.__container.winfo_rooty()+smh-1

                #if event.x_root > lv_maxx or vx+sww >= smw:
                    #vx = smw-sww-1

                #if event.y_root > lv_maxy or vy+swh >= smh:
                    #vy = smh-swh-1

                if not p_moveh:
                    vx = self.winfo_x()
                if not p_movev:
                    vy = self.winfo_y()

                ##################################################
                ## countering
                ##################################################
                self.get_parentapp().app_workspace_hide_mc()
                self.get_parentapp().app_workspace_draw_mc(vx, vy, vx+sww, vy+swh)

        except Others:
            lv_message = 'geom_moving_motion: %s' % (get_estr())
            xprint(lv_message)

    def geom_directmove(self, event, p_moveh=0, p_movev=0 ):
        """ move child on specified values from current coords """

        try:
            if self.__wstate == CHILD_WSTATE_NORMAL:

                vx = self.__ad_geometry['old_x'] + p_moveh
                vy = self.__ad_geometry['old_y'] + p_movev

                self.get_parentapp().app_workspace_hide_mc()
                self.place( x=vx, y=vy )

        except Others:
            lv_message = 'geom_directmove: %s' % (get_estr())
            xprint(lv_message)

    def geom_measure(self):
        """ save child geometry ( dimensions ) """

        self.update_idletasks()

        self.__ad_geometry['min_w'] = max(self.winfo_reqwidth(), self.__ad_geometry['min_w'])
        self.__ad_geometry['min_h'] = max(self.winfo_reqheight(), self.__ad_geometry['min_h'])

    def call_geom_maximize(self, po_event=None):
        """ process geom maximixe """

        self.__parentapp.app_children_maximize(self)

    def geom_maximize(self, event=None):
        """ max window to fill parent workspace """

        try:
            self.__wstate = CHILD_WSTATE_MAXIMIZED

            if self.__uimode == CHILD_UI_MODE_MDI:
                self.__ad_geometry['old_x'] = self.winfo_x()
                self.__ad_geometry['old_y'] = self.winfo_y()

                del self.__ad_resources['header_wstate_btn'].img
                img = PhotoImage(data=pta_icons.get_icon('gv_child_header_restore'))
                self.__ad_resources['header_wstate_btn'].configure(image=img, command=self.call_geom_restore)
                self.__ad_resources['header_wstate_btn'].img = img

            self.lift()
            #self.place(x = 1, y = 1, relwidth=1, width=-2, relheight=1, height=-2)
            self.place(x=0, y=0, relwidth=1, relheight=1)

            if self.__uimode == CHILD_UI_MODE_MDI:
                # configure cursors
                self.__ad_resources['header_bar'].configure( cursor="arrow" )

                self.__anchor_ts.configure( cursor="arrow" )
                self.__anchor_ls.configure( cursor="arrow" )
                self.__anchor_bs.configure( cursor="arrow" )
                self.__anchor_rs.configure( cursor="arrow" )
                self.__anchor_se.configure( cursor="arrow" )
                self.__anchor_sw.configure( cursor="arrow" )

            self.update_idletasks()
        except Others:
            lv_message = 'maximize: %s' % (get_estr())
            xprint(lv_message)

    def call_geom_restore(self, po_event=None):
        """ call geom restore """

        self.__parentapp.app_children_restore(self)

    def geom_restore(self, event=None):
        """ restore child window to original dimensions """

        try:
            self.__wstate = CHILD_WSTATE_NORMAL

            if self.__uimode == CHILD_UI_MODE_MDI:
                del self.__ad_resources['header_wstate_btn'].img
                img = PhotoImage(data=pta_icons.get_icon('gv_child_header_maximize'))
                self.__ad_resources['header_wstate_btn'].configure(image=img, command=self.call_geom_maximize)
                self.__ad_resources['header_wstate_btn'].img = img

            self.place_forget()
            self.place_configure(width=None, height=None)
            self.configure(width=self.__ad_geometry['min_w'], height=self.__ad_geometry['min_h'] )

            ld_geom = self.__ad_geometry
            ld_geom['up_x'] = None
            ld_geom['up_y'] = None

            self.place( x=ld_geom.get('toggle_x', 1),
                        y=ld_geom.get('toggle_y', 1),
                        width=None,
                        height=None )

            if self.__uimode == CHILD_UI_MODE_MDI:
                # configure cursors
                self.__ad_resources['header_bar'].configure( cursor="fleur" )

                self.__anchor_ts.configure( cursor=gl_arrows['v'] )
                self.__anchor_ls.configure( cursor=gl_arrows['h'] )
                self.__anchor_bs.configure( cursor=gl_arrows['v'] )
                self.__anchor_rs.configure( cursor=gl_arrows['h'] )
                self.__anchor_se.configure( cursor=gl_arrows['nwse'] )
                self.__anchor_sw.configure( cursor=gl_arrows['nesw'] )

            self.update_idletasks()
        except Others:
            lv_message = 'restore: %s' % (get_estr())
            xprint(lv_message)

    def get_help( self ):
        """ return help list """

        return self.__help[:]

    def set_help( self, pl_help ):
        """ change child help """

        self.__help = pl_help[:]
        self.child_reconf_help_btn()

    def get_container( self ):
        """ return child container """

        return self.__container

    def get_subchild( self, pv_id ):
        """ get subchild """

        lv_subchildid = self.subchild_generate_id( pv_id )
        return self.__ad_subchildren.get( lv_subchildid, None )

    def get_parentapp( self ):
        """ return ref to parent app """

        return self.__parentapp

    def get_parentwidget( self ):
        """ return ref to parent widget """

        return self.__parentwidget

    def get_options(self):
        """ return options object """

        return self.__options

    def options_get_value(self, option_key, pv_readthss=False, p_copy=False):
        """ get value of spec. option """

        if self.__options is not None:
            return self.__options.get_value(option_key, pv_readthss, p_copy)
        else:
            return None

    def options_set_value(self, option_key, option_value, pb_chdef=False, pb_writethss=False, pb_superset=False):
        """ set value for spec. option """

        if self.__options is not None:
            return self.__options.set_value(option_key, option_value, pb_chdef, pb_writethss, pb_superset)
        else:
            return None

    def options_append_value(self, option_key, option_value):
        """ append value to option-list """

        if self.__options is not None:
            return self.__options.append_value(option_key, option_value)
        else:
            return None

    def get_mcontainer(self):
        """ return object for parent of messageboxes """

        return self.get_workspace()

    def child_message(self, pv_type, pv_message, **kw):
        """ show some message """

        lv_silence = kw.get('silence', False)
        if lv_silence not in (True, False):
            lv_silence = False

        lv_detail = kw.get('detail', None)
        lw_parent = kw.get('parent', None)

        ld_kw = {}
        if lv_detail is not None:
            ld_kw['detail'] = lv_detail
        ld_kw['parent'] = novl(lw_parent, self.get_workspace())

        lv_reporter = self.get_title().strip()
        if pv_type == 'warning':
            lv_header = '[warning]'
            lf_func = messagebox.showwarning
        elif pv_type == 'error':
            lv_header = '[error]'
            lf_func = messagebox.showerror
        else:
            lv_header = '[info]'
            lf_func = messagebox.showinfo

        lv_message = '%s - %s: %s' % (lv_header, lv_reporter, pv_message)

        xprint(lv_message)
        if lv_detail is not None:
            xprint('detail:\n%s'%lv_detail)

        lo_parentapp = self.get_parentapp()
        if lo_parentapp and lo_parentapp.get_uimode() == APP_UI_MODE_BAT:
            if not lv_silence:
                self.child_logging(_('Batch-mode: auto-accept !!!'))
        elif not lv_silence:
            lf_func(lv_header, pv_message, **ld_kw)

        lw_log = self.get_resource_item('log')
        if lw_log:
            lw_log.storedatawidgetendl1mark('pos1')

        self.child_logging(lv_message, pb_forced=True)
        if lv_detail is not None:
            self.child_logging('detail:\n%s'%lv_detail, pb_at=False, pb_forced=True)

        if lw_log:
            lw_log.storedatawidgetendl1mark('pos2')
            lw_log.tag_data('!%s' % pv_type, 'pos1', 'pos2')

    def child_showwarning(self, pv_message, **kw):
        """ show some warning """

        self.child_message('warning', pv_message, **kw)

    def child_showerror(self, pv_message, **kw):
        """ show some error """

        self.child_message('error', pv_message, **kw)

    def child_showinfo(self, pv_message, **kw):
        """ show some info """

        kw.setdefault('silence', True)
        self.child_message('info', pv_message, **kw)

    def child_ask(self, pv_type, pv_message, **kw):
        """ask... from messagebox"""

        if pv_type == 'okcancel':
            lf_subprogram = messagebox.askokcancel
        elif pv_type == 'yesno':
            lf_subprogram = messagebox.askyesno
        elif pv_type == 'yesnocancel':
            lf_subprogram = messagebox.askyesnocancel
        else:
            lf_subprogram = messagebox.askokcancel

        ld_kw = kw.copy()
        if 'title' in ld_kw:
            lv_title = _(ld_kw.pop('title'))
        else:
            lv_title = _('Confirm')

        if 'parent' not in ld_kw:
            ld_kw['parent'] = self.get_mcontainer()
        lv_detail = kw.get('detail', None)

        lo_parentapp = self.get_parentapp()
        if lo_parentapp and lo_parentapp.get_uimode() == APP_UI_MODE_BAT:
            self.child_logging(_('Batch-mode: auto-accept !!!'))
            lv_out = True
        else:
            lv_out = lf_subprogram(lv_title,
                                   pv_message,
                                   **ld_kw)

        lw_log = self.get_resource_item('log')
        if lw_log:
            lw_log.storedatawidgetendl1mark('pos1')

        # out data
        self.child_logging('%s' % pv_type)
        self.child_logging(_('Ask:'), pb_at=False)
        self.child_logging(lv_title, pb_at=False)
        self.child_logging(pv_message, pb_at=False)
        if lv_detail is not None:
            self.child_logging('Detail:\n%s'%lv_detail, pb_at=False)
        self.child_logging(_('Answer:'), pb_at=False)
        self.child_logging('%s' % lv_out, pb_at=False)

        if lw_log:
            lw_log.storedatawidgetendl1mark('pos2')
            lw_log.tag_data('!ask', 'pos1', 'pos2')

        return lv_out

    def child_askokcancel(self, pv_message, **kw):
        """ask ok/cancel"""

        return self.child_ask('okcancel', pv_message, **kw)

    def child_askyesno(self, pv_message, **kw):
        """ask yes/no"""

        return self.child_ask('yesno', pv_message, **kw)

    def child_askyesnocancel(self, pv_message, **kw):
        """ask yes/no/cancel"""

        return self.child_ask('yesnocancel', pv_message, **kw)

    def child_c2c_interaction(self, **kw):
        """ process interaction between children """

        pass

    def optwindow_prepare_optopts(self):
        """ return dict with options attrs for displaing """

        ld_optopts = {}

        return ld_optopts

    def optwindow_prepare_excluded_groups(self):
        """ return list of groups that we want to hide"""

        ll_exlist = [OPTGROUP_UNASSIGNED]

        return ll_exlist

    def optwindow_prepare_excluded_options(self):
        """ return list of options that we want to hide"""

        ll_exlist = []

        return ll_exlist

    def optwindow_post_optnotebook(self, pw_toplevel, pw_frame, pd_widgets):
        """ process additional conf. for options widgets on opt.window """

        pass

    def optwindow_post_window(self):
        """ process here some routines that necessary after changing some opt.."""

        self.__options.fill_thss()

    def call_options_window(self, event=None):
        """ show child options as Notebook widget """

        self.child_deactivate()
        try:
            ld_optopts  = self.optwindow_prepare_optopts()
            ll_exgroups = self.optwindow_prepare_excluded_groups()
            ll_exopts   = self.optwindow_prepare_excluded_options()

            if self.__options.check_optnotebook(excluded_groups=ll_exgroups,
                                                excluded_options=ll_exopts):
                lt_logos = self.get_parentapp().get_logos_data()

                lw_toplevel, lw_frame = toplevel_header( self.get_mcontainer(),
                                                         title=_('Options'),
                                                         logopath=lt_logos[0],
                                                         logoname=lt_logos[1],
                                                         noresize=1
                                                       )

                ld_items = self.__options.show_optnotebook( lw_frame,
                                                            ld_optopts,
                                                            excluded_groups=ll_exgroups,
                                                            excluded_options=ll_exopts
                                                          )

                self.__options.force_rules()

                lw_toplevel.protocol("WM_DELETE_WINDOW", lambda w=lw_toplevel: self.__options.notice_of_the_eviction(w, True))

                self.optwindow_post_optnotebook(lw_toplevel, lw_frame, ld_items)

                toplevel_footer(lw_toplevel, self.get_mcontainer(), min_width=50, min_height=50)
            else:
                self.child_showwarning(_('No available options !'))

        except Others:
            lv_message = 'failed to call options window: %s' % (get_estr())
            xprint(lv_message)

        self.optwindow_post_window()
        self.child_activate()

        # use this if you bind routine to some widgets
        return "break"