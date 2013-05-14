#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# client.py - Somewhat higher-level GUI_RPC API for BOINC core client
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

# Based on client/boinc_cmd.cpp

import rpc
import socket
import hashlib
from functools import total_ordering
from xml.etree import ElementTree


GUI_RPC_PASSWD_FILE = "/etc/boinc-client/gui_rpc_auth.cfg"

def setattrs_from_xml(obj, xml, attrfuncdict={}):
    if not isinstance(xml, ElementTree.Element):
        xml = ElementTree.fromstring(xml)
    for e in list(xml):
        if hasattr(obj, e.tag):
            attr = getattr(obj, e.tag)
            attrfunc = attrfuncdict.get(e.tag, None)
            if not attrfunc:
                if   isinstance(attr, int):   attrfunc = int
                elif isinstance(attr, float): attrfunc = float
                elif isinstance(attr, bool):  attrfunc = bool
                else:                         attrfunc = str
            setattr(obj, e.tag, attrfunc(e.text))
    return obj


@total_ordering
class VersionInfo(object):
    def __init__(self, major=0, minor=0, release=0):
        self.major     = major
        self.minor     = minor
        self.release   = release

    @classmethod
    def parse(cls, xml):
        return setattrs_from_xml(cls(), xml)

    @property
    def _tuple(self):
        return  (self.major, self.minor, self.release)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._tuple == other._tuple

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._tuple > other._tuple

    def __str__(self):
        return "%d.%d.%d" % (self.major, self.minor, self.release)

    def __repr__(self):
        return "%s%r" % (self.__class__.__name__, self._tuple)


class CcStatus(object):
    def __init__(self):
        self.network_status         = -1    #// values: NETWORK_STATUS_*
        self.ams_password_error     = False
        self.manager_must_quit      = False
        self.task_suspend_reason    = -1    #// bitmap, see common_defs.h
        self.task_mode              = -1    #// always/auto/never; see common_defs.h
        self.task_mode_perm         = -1    #// same, but permanent version
        self.task_mode_delay        =  0.0  #// time until perm becomes actual
        self.network_suspend_reason = -1
        self.network_mode           = -1
        self.network_mode_perm      = -1
        self.network_mode_delay     =  0.0
        self.gpu_suspend_reason     = -1
        self.gpu_mode               = -1
        self.gpu_mode_perm          = -1
        self.gpu_mode_delay         =  0.0
        self.disallow_attach        = False
        self.simple_gui_only        = False

    @classmethod
    def parse(cls, xml):
        return setattrs_from_xml(cls(), xml)

    def __str__(self):
        buf = '%s:\n' % self.__class__.__name__
        for attr in self.__dict__:
            buf += '\t%s\t%r\n' % (attr, getattr(self, attr))
        return buf


class BoincClient(object):

    def __init__(self, host="", passwd=None):
        host = host.split(':', 1)

        self.hostname   = host[0]
        self.port       = int(host[1]) if len(host)==2 else 0
        self.passwd     = passwd
        self.rpc        = rpc.Rpc()
        self.version    = None
        self.authorized = False

        # Informative, not authoritative. Records status of *last* RPC call,
        # but does not infer success about the *next* one.
        # Thus, it should be read *after* an RPC call, not prior to one
        self.connected = False

    def __enter__(self): self.connect(); return self
    def __exit__(self, *args): self.disconnect()

    def connect(self):
        try:
            self.rpc.connect(self.hostname, self.port)
            self.connected = True
        except socket.error:
            self.connected = False
            return
        self.authorized = self.authorize(self.passwd)
        self.version = self.exchange_versions()

    def disconnect(self):
        self.rpc.disconnect()

    def authorize(self, password):
        ''' Request authorization. If password is None and we are connecting
            to localhost, try to read password from the local config file
            GUI_RPC_PASSWD_FILE. If file can't be read (not found or no
            permission to read), try to authorize with a blank password.
            If authorization is requested and fails, all subsequent calls
            will be refused with socket.error 'Connection reset by peer' (104).
            Since most local calls do no require authorization, do not attempt
            it if you're not sure about the password.
        '''
        if password is None and not self.hostname:
            password = read_gui_rpc_password() or ""
        nonce = ElementTree.fromstring(self.rpc.call('<auth1/>')).text
        hash = hashlib.md5('%s%s' % (nonce, password)).hexdigest().lower()
        reply = ElementTree.fromstring(
            self.rpc.call('<auth2><nonce_hash>%s</nonce_hash></auth2>' % hash))

        if reply.tag == 'authorized':
            return True
        else:
            print ElementTree.tostring(reply)
            return False

    def exchange_versions(self):
        return VersionInfo.parse(self.rpc.call('<exchange_versions/>'))

    def get_cc_status(self):
        if not self.connected: self.connect()
        try:
            return CcStatus.parse(self.rpc.call('<get_cc_status/>'))
        except socket.error:
            self.connected = False


def read_gui_rpc_password():
    ''' Read password string from GUI_RPC_PASSWD_FILE file, trim the last CR
        (if any), and return it
    '''
    try:
        with open(GUI_RPC_PASSWD_FILE, 'r') as f:
            buf = f.read()
            if buf.endswith('\n'): return buf[:-1]  # trim last CR
            else: return buf
    except IOError:
        # Permission denied or File not found.
        pass


if __name__ == '__main__':
    with BoincClient() as boinc:
        print boinc.authorized
        print boinc.version
        print boinc.get_cc_status()
