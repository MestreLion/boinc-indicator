#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# monitor.py - App Indicator for monitoring and managing BOINC'
#
#    Copyright (C) 2013 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>

# Based on clientgui/BOINCTaskBar.{h,cpp}

import sys
import os.path as osp
import webbrowser

from gi.repository import Gtk, GLib, AppIndicator3

import client

# gettext stub, for future translations
def _(text, *args):
    if args:
        return text % args
    else:
        return text

__all__     = ['BoincIndicator']
__version__ = '0.1'
__apptag__  = 'boinc-monitor'
__appname__ = _('BOINC Monitor')
__appdesc__ = _('App Indicator for monitoring and managing BOINC')
__author__  = 'Rodrigo Silva'
__url__     = 'http://github.com/MestreLion/boinc-indicator'
__date__    = '2013-05-08'
__updated__ = '2013-05-08'




class BoincIndicator(object):
    def __init__(self, theme_path="", refresh=3):
        self.theme_path = osp.abspath(theme_path or
                                      osp.join(osp.dirname(__file__),"images"))
        self._refresh = refresh
        self._timerid = 0

        self.icon           = __apptag__
        self.icon_normal    = __apptag__ + '-normal'
        self.icon_error     = __apptag__ + '-error'
        self.icon_pause_cpu = __apptag__ + '-pause'
        self.icon_pause_gpu = __apptag__ + '-pause-gpu'

        self.task_run     = 'task_green.png'
        self.task_wait    = 'task_yellow.png'
        self.task_suspend = 'task_red'

        self.label_prefix = _('Boinc')
        self.label_normal = _('running')
        self.label_pause  = _('suspended')
        self.label_error  = _('disconnected')

        self.boinc = client.BoincClient()

        self.ind = AppIndicator3.Indicator.new_with_path(
                            __apptag__,
                            self.icon_normal,
                            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
                            self.theme_path)

        self.ind.set_title(__appname__)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon(self.icon_error)

        self.menu = {}

        menu_items = [
            ['website',            _('Open BOINC _Web...')],
            ['manager',            _('Open BOINC _Manager...')],
            [],
            ['status_version',     ""],
            ['status_cpu',         ""],
            ['status_gpu',         ""],
            ['status_net',         ""],
            [],
            ['suspend_resume_cpu', _('_Snooze'),     Gtk.CheckMenuItem],
            ['suspend_resume_gpu', _('Snooze _GPU'), Gtk.CheckMenuItem],
            [],
            ['about',              _('_About %s...' % __appname__)],
            [],
            ['quit',               _('_Quit')],
        ]
        gtkmenu = Gtk.Menu()
        for item in menu_items:
            if item:
                cls = item[2] if len(item) >= 3 else Gtk.MenuItem
                itm = cls.new_with_mnemonic(item[1])
                hdl = getattr(self, 'handler_' + item[0], None)
                itm.connect("activate", hdl or self.handler_generic)
                if item[0].startswith('status'):
                    itm.set_sensitive(False)
                gtkmenu.append(itm)
                self.menu[item[0]] = itm
            else:
                gtkmenu.append(Gtk.SeparatorMenuItem())

        gtkmenu.show_all()
        self.ind.set_menu(gtkmenu)

    # TODO:
    # refresh rate control is premature over-engineering that will likely
    # be removed after first commit, and only come back in distant future.
    @property
    def refresh(self):
        return self._refresh

    @refresh.setter
    def refresh(self, value):
        if self._timerid and not value == self._refresh:
            GLib.source_remove(self._timerid)

        if value:
            self.update_status()
            self._timerid = GLib.timeout_add_seconds(self.refresh,
                                                     self.update_status)


    def main(self):
        #FIXME: make damn sure Indicator have found icons and it's working
        #       before entering Gtk.main()! An invisible indicator has no means
        #       to exit app, and KeyboardInterrupt does not work with Gtk.main()
        #       See: https://bugzilla.gnome.org/show_bug.cgi?id=622084
        self.boinc.connect()
        self.update_status()
        self._timerid = GLib.timeout_add_seconds(self.refresh,
                                                 self.update_status)
        Gtk.main()


    def quit(self):
        Gtk.main_quit()
        self.boinc.disconnect()


    def handler_generic(self, src):
        pass


    def handler_website(self, src):
        webbrowser.open('http://boinc.berkeley.edu')


    def suspend_resume(self, src, component):
        if src.get_active():
            self.boinc.set_mode(component, client.RunMode.NEVER, 3600)
        else:
            self.boinc.set_mode(component, client.RunMode.RESTORE)
        self.update_status()


    def handler_suspend_resume_cpu(self, src):
        self.suspend_resume(src, 'cpu')


    def handler_suspend_resume_gpu(self, src):
        self.suspend_resume(src, 'gpu')


    def handler_about(self, src):
        #TODO: prevent opening multiple times, fix icon, fix launcher, disable minimize
        about = Gtk.AboutDialog()
        about.set_name(__appname__)
        about.set_version(str(__version__))
        about.set_logo_icon_name('boincmgr')
        about.set_comments(__appdesc__)
        about.set_website(__url__)
        about.set_website_label(_('%s Website' % __appname__))
        about.set_authors([__author__])
        about.set_translator_credits(_("translator-credits"))
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_copyright('Copyright (C) 2013 Rodrigo Silva')
        about.run()
        about.destroy()


    def handler_quit(self, src):
        self.quit()


    def check_set_active(self, tag, value):
        ''' A replacement for Gtk.CheckMenuItem.set_active() that blocks
            signals, so callbacks are triggered only by a user click UI event.
            Ugly workaround to avoid undesirable loops and toggling
        '''
        handler = getattr(self, 'handler_' + tag)
        self.menu[tag].handler_block_by_func(handler)
        self.menu[tag].set_active(value)
        self.menu[tag].handler_unblock_by_func(handler)


    def update_status(self):
        ''' Updates the UI according to boinc client status '''

        status = self.boinc.get_cc_status()
        if not self.boinc.connected:
            self.menu['suspend_resume_cpu'].set_sensitive(False)
            self.menu['suspend_resume_gpu'].set_sensitive(False)
            self.menu['status_version'].set_label('Not connected')
            self.menu['status_cpu'].hide()
            self.menu['status_gpu'].hide()
            self.menu['status_net'].hide()
            self.ind.set_icon(self.icon_error)
        else:
            # Set UI for 'connected'
            self.menu['suspend_resume_cpu'].set_sensitive(True)
            self.menu['status_version'].set_label(_('BOINC client version: %s'
                                                    % self.boinc.version))

            # Status evaluation is a complex beast: task_mode instantly reports
            # what client is *set* to, but not if it's *actually* running wus.
            # For example, it might be set to AUTO and be suspended due to
            # BATTERIES or USER_ACTIVE. task_suspend_reason is more accurate,
            # but it does not reflect changes instantly, it can take >1s. Yes,
            # meanwhile the XML output from RPC call shows inconsistent status.
            # Try: boinccmd --set_run_mode never && boinccmd --get_cc_status
            # That's why original taskbar chooses task_mode for icon (responsive
            # updates, but only catches NEVER) and task_suspend_reason for its
            # tooltip status description. It's a sensible compromise.
            # []Snooze/[x]Snooze/Resume tristate also have a complex mechanism.
            # Here, icon and status labels are locked together (not ideal), but
            # icon is both responsive AND catches any suspension. But currently
            # lacks the tristate menu.
            if (status.task_mode == client.RunMode.NEVER or
                (status.task_mode == client.RunMode.AUTO and
                 status.task_suspend_reason not in
                    [client.SuspendReason.NOT_SUSPENDED,
                     client.SuspendReason.CPU_THROTTLE])):

                # Set UI for 'cpu suspended'
                self.check_set_active('suspend_resume_cpu', True)
                self.check_set_active('suspend_resume_gpu', False)
                self.menu['suspend_resume_gpu'].set_sensitive(False)
                self.menu['status_cpu'].set_label(
                    '%s%s' % (
                    _("Computing is suspended"),
                    " - " + client.SuspendReason.name(status.task_suspend_reason)
                    if status.task_suspend_reason != client.SuspendReason.NOT_SUSPENDED
                    else ""))
                self.menu['status_gpu'].hide()
                self.menu['status_net'].hide()
                self.ind.set_icon(self.icon_pause_cpu)

            else:

                # Set UI for 'cpu active'
                self.check_set_active('suspend_resume_cpu', False)
                self.menu['suspend_resume_gpu'].set_sensitive(True)
                self.menu['status_cpu'].set_label(_("Computing is enabled"))

                if (status.gpu_mode == client.RunMode.NEVER or
                    (status.gpu_mode == client.RunMode.AUTO and
                     status.gpu_suspend_reason !=
                     client.SuspendReason.NOT_SUSPENDED)):
                    # Set UI for 'gpu suspended'
                    self.check_set_active('suspend_resume_gpu', True)
                    self.menu['status_gpu'].set_label(
                        '%s%s' % (
                        _("GPU computing is suspended"),
                        " - " + client.SuspendReason.name(status.gpu_suspend_reason)
                        if status.gpu_suspend_reason != client.SuspendReason.NOT_SUSPENDED
                        else ""))
                    self.ind.set_icon(self.icon_pause_gpu)

                else:

                    # TODO: Must test if there *IS* a GPU (CcState.have_gpu())
                    # Set UI for 'gpu active'
                    self.check_set_active('suspend_resume_gpu', False)
                    self.menu['status_gpu'].set_label(_("GPU computing is enabled"))
                    self.ind.set_icon(self.icon_normal)

                if (status.network_mode == client.RunMode.NEVER or
                    (status.network_mode == client.RunMode.AUTO and
                     status.network_suspend_reason !=
                     client.SuspendReason.NOT_SUSPENDED)):
                    # Set UI for 'net suspended'
                    self.menu['status_net'].set_label(
                        '%s%s' % (
                        _("Network activity is suspended"),
                        " - " + client.SuspendReason.name(status.network_suspend_reason)
                        if status.network_suspend_reason != client.SuspendReason.NOT_SUSPENDED
                        else ""))
                else:
                    # Set UI for 'net active'
                    self.menu['status_net'].set_label(_("Network is enabled"))

                # (re-)show menus for 'cpu active'
                self.menu['status_gpu'].show()
                self.menu['status_net'].show()

            # (re-)show menus for 'connected' as last action,
            # to avoid any visual glitches
            self.menu['status_cpu'].show()

        return True  # returning False would deactivate update timer




if __name__ == "__main__":
    GLib.set_application_name(__appname__)
    GLib.set_prgname(__apptag__)
    ind = BoincIndicator()
    sys.exit(ind.main())
