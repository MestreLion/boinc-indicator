#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rpc.py - Generic RPC Somewhat higher-level GUI_RPC API for BOINC core client
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

# A replacement of gui_rpc_client for basic RPC calls, with a sane API

import socket
from xml.etree import ElementTree

GUI_RPC_HOSTNAME    = None  # localhost
GUI_RPC_PORT        = 31416
GUI_RPC_TIMEOUT     = 30

class Rpc(object):
    ''' Class to perform GUI RPC calls to a BOINC core client.
        Usage in a context manager ('with' block) is recommended to ensure
        disconnect() is called. Using the same instance for all calls is also
        recommended so it reuses the same socket connection
        '''
    def __init__(self, hostname="", port=0, timeout=0, text_output=False):
        self.hostname = hostname
        self.port     = port
        self.timeout  = timeout
        self.sock = None
        self.text_output = text_output

    @property
    def sockargs(self):
        return (self.hostname, self.port, self.timeout)

    def __enter__(self): self.connect(*self.sockargs); return self
    def __exit__(self, *args): self.disconnect()

    def connect(self, hostname="", port=0, timeout=0):
        ''' Connect to (hostname, port) with timeout in seconds.
            Hostname defaults to None (localhost), and port to 31416
            Calling multiple times will disconnect previous connection (if any),
            and (re-)connect to host.
        '''
        if self.sock:
            self.disconnect()

        self.hostname = hostname or GUI_RPC_HOSTNAME
        self.port     = port     or GUI_RPC_PORT
        self.timeout  = timeout  or GUI_RPC_TIMEOUT

        self.sock = socket.create_connection(self.sockargs[0:2], self.sockargs[2])

    def disconnect(self):
        ''' Disconnect from host. Calling multiple times is OK (idempotent)
        '''
        if self.sock:
            self.sock.close()
            self.sock = None

    def call(self, request, text_output=None):
        ''' Do an RPC call. Pack and send the XML request and return the
            unpacked reply. request can be either plain XML text or a
            xml.etree.ElementTree.Element object. Return ElementTree.Element
            or XML text according to text_output flag.
            Will auto-connect if not connected.
        '''
        if text_output is None:
            text_output = self.text_output

        if not self.sock:
            self.connect(*self.sockargs)

        if not isinstance(request, ElementTree.Element):
            request = ElementTree.fromstring(request)

        # pack request
        end = '\003'
        req = "<boinc_gui_rpc_request>\n%s\n</boinc_gui_rpc_request>\n%s" \
            % (ElementTree.tostring(request).replace(' />','/>'), end)

        try:
            self.sock.sendall(req)
        except (socket.error, socket.herror, socket.gaierror, socket.timeout):
            raise

        req = ""
        while True:
            try:
                buf = self.sock.recv(8192)
                if not buf:
                    raise socket.error("No data from socket")
            except socket.error:
                raise
            n = buf.find(end)
            if not n == -1: break
            req += buf
        req += buf[:n]

        # unpack reply (remove root tag, ie: first and last lines)
        req = '\n'.join(req.strip().rsplit('\n')[1:-1])

        if text_output:
            return req
        else:
            return ElementTree.fromstring(req)


if __name__ == '__main__':
    with Rpc(text_output=True) as rpc:
        print rpc.call('<exchange_versions/>')
        print rpc.call('<get_cc_status/>')
        print rpc.call('<get_host_info/>')
        print rpc.call('<get_results/>')
        print rpc.call('<run_benchmarks/>')
