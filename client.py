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
    ''' Helper to set values for attributes of a class instance by mapping
        matching tags from a XML file.
        attrfuncdict is a dict of functions to customize value data type of
        each attribute. It falls back to simple int/float/bool/str detection
        based on values defined in __init__(). This would not be needed if
        Boinc used standard RPC protocol, which includes data type in XML.
    '''
    if not isinstance(xml, ElementTree.Element):
        xml = ElementTree.fromstring(xml)
    for e in list(xml):
        if hasattr(obj, e.tag):
            attr = getattr(obj, e.tag)
            attrfunc = attrfuncdict.get(e.tag, None)
            if attrfunc is None:
                if   isinstance(attr, bool):  attrfunc = parse_bool
                elif isinstance(attr, int):   attrfunc = parse_int
                elif isinstance(attr, float): attrfunc = parse_float
                else:                         attrfunc = parse_str
            setattr(obj, e.tag, attrfunc(e))
    return obj


def parse_bool(e):
    ''' Helper to convert ElementTree.Element.text to boolean.
        Treat '<foo/>' (and '<foo>[[:blank:]]</foo>') as True
        Treat '0' and 'false' as False
    '''
    if e.text is None:
        return True
    else:
        return bool(e.text) and not e.text.strip().lower() in ('0', 'false')


def parse_int(e):
    ''' Helper to convert ElementTree.Element.text to integer.
        Treat '<foo/>' (and '<foo></foo>') as 0
    '''
    return 0 if e.text is None else int(e.text.strip())


def parse_float(e):
    ''' Helper to convert ElementTree.Element.text to float. '''
    return 0.0 if e.text is None else float(e.text.strip())


def parse_str(e):
    ''' Helper to convert ElementTree.Element.text to string. '''
    return "" if e.text is None else e.text.strip()


class Enum(object):
    UNKNOWN                =   -1  # Not in original API

    @classmethod
    def name(cls, value):
        ''' Quick-and-dirty fallback for getting the "name" of an enum item '''

        # value as string, if it matches an enum attribute.
        # Allows short usage as Enum.name("VALUE") besides Enum.name(Enum.VALUE)
        if hasattr(cls, str(value)):
            return cls.name(getattr(cls, value, None))

        # value not handled in subclass name()
        for k, v in cls.__dict__.items():
            if v == value:
                return k.lower().replace('_', ' ')

        # value not found
        return cls.name(Enum.UNKNOWN)


class NetworkStatus(Enum):
    ''' Values of "network_status" '''
    ONLINE                 =    0  #// have network connections open
    WANT_CONNECTION        =    1  #// need a physical connection
    WANT_DISCONNECT        =    2  #// don't have any connections, and don't need any
    LOOKUP_PENDING         =    3  #// a website lookup is pending (try again later)

    @classmethod
    def name(cls, v):
        if   v == cls.UNKNOWN:         return "unknown"
        elif v == cls.ONLINE:          return "online"  # misleading
        elif v == cls.WANT_CONNECTION: return "need connection"
        elif v == cls.WANT_DISCONNECT: return "don't need connection"
        elif v == cls.LOOKUP_PENDING:  return "reference site lookup pending"
        else: return super(NetworkStatus, cls).name(v)


class SuspendReason(Enum):
    ''' bitmap defs for task_suspend_reason, network_suspend_reason
        Note: doesn't need to be a bitmap, but keep for compatibility
    '''
    NOT_SUSPENDED          =    0  # Not in original API
    BATTERIES              =    1
    USER_ACTIVE            =    2
    USER_REQ               =    4
    TIME_OF_DAY            =    8
    BENCHMARKS             =   16
    DISK_SIZE              =   32
    CPU_THROTTLE           =   64
    NO_RECENT_INPUT        =  128
    INITIAL_DELAY          =  256
    EXCLUSIVE_APP_RUNNING  =  512
    CPU_USAGE              = 1024
    NETWORK_QUOTA_EXCEEDED = 2048
    OS                     = 4096
    WIFI_STATE             = 4097
    BATTERY_CHARGING       = 4098
    BATTERY_OVERHEATED     = 4099

    @classmethod
    def name(cls, v):
        if   v == cls.UNKNOWN:                return "unknown reason"
        elif v == cls.BATTERIES:              return "on batteries"
        elif v == cls.USER_ACTIVE:            return "computer is in use"
        elif v == cls.USER_REQ:               return "user request"
        elif v == cls.TIME_OF_DAY:            return "time of day"
        elif v == cls.BENCHMARKS:             return "CPU benchmarks in progress"
        elif v == cls.DISK_SIZE:              return "need disk space - check preferences"
        elif v == cls.NO_RECENT_INPUT:        return "no recent user activity"
        elif v == cls.INITIAL_DELAY:          return "initial delay"
        elif v == cls.EXCLUSIVE_APP_RUNNING:  return "an exclusive app is running"
        elif v == cls.CPU_USAGE:              return "CPU is busy"
        elif v == cls.NETWORK_QUOTA_EXCEEDED: return "network bandwidth limit exceeded"
        elif v == cls.OS:                     return "requested by operating system"
        elif v == cls.WIFI_STATE:             return "not connected to WiFi network"
        elif v == cls.BATTERY_CHARGING:       return "battery is recharging"
        elif v == cls.BATTERY_OVERHEATED:     return "battery is overheated"
        else: return super(SuspendReason, cls).name(v)


class RunMode(Enum):
    ''' Run modes for CPU, GPU, network,
        controlled by Activity menu and snooze button
    '''
    ALWAYS                 =    1
    AUTO                   =    2
    NEVER                  =    3
    RESTORE                =    4  #// restore permanent mode - used only in set_X_mode() GUI RPC

    @classmethod
    def name(cls, v):
        # all other modes use the fallback name
        if v == cls.AUTO: return "according to prefs"
        else: return super(RunMode, cls).name(v)


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
        self.network_status         = NetworkStatus.UNKNOWN
        self.ams_password_error     = False
        self.manager_must_quit      = False

        self.task_suspend_reason    = SuspendReason.UNKNOWN  #// bitmap
        self.task_mode              = RunMode.UNKNOWN
        self.task_mode_perm         = RunMode.UNKNOWN        #// same, but permanent version
        self.task_mode_delay        = 0.0                    #// time until perm becomes actual

        self.network_suspend_reason = SuspendReason.UNKNOWN
        self.network_mode           = RunMode.UNKNOWN
        self.network_mode_perm      = RunMode.UNKNOWN
        self.network_mode_delay     = 0.0

        self.gpu_suspend_reason     = SuspendReason.UNKNOWN
        self.gpu_mode               = RunMode.UNKNOWN
        self.gpu_mode_perm          = RunMode.UNKNOWN
        self.gpu_mode_delay         = 0.0

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


class Result(object):
    def __init__(self):
        self.name                         = ""
        self.wu_name                      = ""
        self.version_num                  = 0
        self.plan_class                   = ""
        self.project_url                  = ""
        self.report_deadline              = 0.0    # seconds since epoch
        self.received_time                = 0.0    # seconds since epoch
        self.ready_to_report              = False
        self.got_server_ack               = False
        self.final_cpu_time               = 0.0
        self.final_elapsed_time           = 0.0
        self.state                        = 0
        self.scheduler_state              = 0
        self.exit_status                  = 0
        self.signal                       = 0
        self.suspended_via_gui            = False
        self.project_suspended_via_gui    = False
        self.coproc_missing               = False
        self.scheduler_wait               = False
        self.scheduler_wait_reason        = ""
        self.network_wait                 = False

        #// the following defined if active
        self.active_task                  = False
        self.active_task_state            = 0
        self.app_version_num              = 0
        self.slot                         = -1
        self.pid                          = 0
        self.checkpoint_cpu_time          = 0.0
        self.current_cpu_time             = 0.0
        self.fraction_done                = 0.0
        self.elapsed_time                 = 0.0
        self.swap_size                    = 0.0
        self.working_set_size_smoothed    = 0.0
        self.estimated_cpu_time_remaining = 0.0    #// actually, estimated elapsed time remaining
        self.too_large                    = False
        self.needs_shmem                  = False
        self.edf_scheduled                = False

        self.graphics_exec_path           = ""
        self.web_graphics_url             = ""
        self.remote_desktop_addr          = ""
        self.slot_path                    = ""    #// only present if graphics_exec_path is
        self.resources                    = ""

        self.app                          = None  # APP*
        self.wup                          = None  # WORKUNIT*
        self.project                      = None  # PROJECT*
        self.avp                          = None  # APP_VERSION*

    @classmethod
    def parse(cls, xml):
        if not isinstance(xml, ElementTree.Element):
            xml = ElementTree.fromstring(xml)

        # parse main XML
        result = setattrs_from_xml(cls(), xml)

        # parse '<active_task>' children
        active_task = xml.find('active_task')
        if active_task is None:
            result.active_task = False  # already the default after __init__()
        else:
            result.active_task = True   # already the default after main parse
            result = setattrs_from_xml(result, active_task)

        return result

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
        self.rpc        = rpc.Rpc(text_output=False)
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
        nonce = self.rpc.call('<auth1/>').text
        hash = hashlib.md5('%s%s' % (nonce, password)).hexdigest().lower()
        reply = self.rpc.call('<auth2><nonce_hash>%s</nonce_hash></auth2>' % hash)

        if reply.tag == 'authorized':
            return True
        else:
            return False

    def exchange_versions(self):
        ''' Return VersionInfo instance with core client version info '''
        return VersionInfo.parse(self.rpc.call('<exchange_versions/>'))

    def get_cc_status(self):
        ''' Return CcStatus instance containing basic status, such as
            CPU / GPU / Network active/suspended, etc
        '''
        if not self.connected: self.connect()
        try:
            return CcStatus.parse(self.rpc.call('<get_cc_status/>'))
        except socket.error:
            self.connected = False

    def get_tasks(self):
        ''' Same as get_results(active_only=False) '''
        return self.get_results(False)

    def get_results(self, active_only=False):
        ''' Get a list of results.
            Those that are in progress will have information such as CPU time
            and fraction done. Each result includes a name;
            Use CC_STATE::lookup_result() to find this result in the current static state;
            if it's not there, call get_state() again.
        '''
        reply = self.rpc.call("<get_results><active_only>%d</active_only></get_results>"
                               % (1 if active_only else 0))
        if not reply.tag == 'results':
            return []

        results = []
        for item in list(reply):
            results.append(Result.parse(item))

        return results


    def set_mode(self, component, mode, duration=0):
        ''' Do the real work of set_{run,gpu,network}_mode()
            This method is not part of the original API.
            Valid components are 'run' (or 'cpu'), 'gpu', 'network' (or 'net')
        '''
        component = component.replace('cpu','run')
        component = component.replace('net','network')
        try:
            reply = self.rpc.call("<set_%s_mode>"
                                  "<%s/><duration>%f</duration>"
                                  "</set_%s_mode>"
                                  % (component,
                                     RunMode.name(mode).lower(), duration,
                                     component))
            return (reply.tag == 'success')
        except socket.error:
            return False

    def set_run_mode(self, mode, duration=0):
        ''' Set the run mode (RunMode.NEVER/AUTO/ALWAYS/RESTORE)
            NEVER will suspend all activity, including CPU, GPU and Network
            AUTO will run according to preferences.
            If duration is zero, mode is permanent. Otherwise revert to last
            permanent mode after duration seconds elapse.
        '''
        return self.set_mode('cpu', mode, duration)

    def set_gpu_mode(self, mode, duration=0):
        ''' Set the GPU run mode, similar to set_run_mode() but for GPU only
        '''
        return self.set_mode('gpu', mode, duration)

    def set_network_mode(self, mode, duration=0):
        ''' Set the Network run mode, similar to set_run_mode()
            but for network activity only
        '''
        return self.set_mode('net', mode, duration)

    def run_benchmarks(self):
        ''' Run benchmarks. Computing will suspend during benchmarks '''
        return self.rpc.call('<run_benchmarks/>').tag == "success"

    def quit(self):
        ''' Tell the core client to exit '''
        if self.rpc.call('<quit/>').tag == "success":
            self.connected = False
            return True
        return False


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
    import time
    with BoincClient() as boinc:
        print boinc.connected
        print boinc.authorized
        print boinc.version
        print boinc.get_cc_status()
        for i, task in enumerate(boinc.get_tasks()):
            print i+1, task
        print boinc.run_benchmarks()
        print boinc.set_run_mode(RunMode.NEVER, 6)
        time.sleep(7)
        print boinc.set_gpu_mode(RunMode.NEVER, 6)
        time.sleep(7)
        print boinc.set_network_mode(RunMode.NEVER, 6)
