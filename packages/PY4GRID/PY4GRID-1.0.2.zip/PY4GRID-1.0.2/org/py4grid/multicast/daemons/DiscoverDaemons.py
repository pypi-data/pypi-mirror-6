"""
PY4GRID : a little framework to simule multiprocessing over a lot of computers
Copyright (C) 2014  João Jorge Pereira Farias Junior
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'dev'

import multiprocessing as multi
import os
import threading as trd
import time
import signal
import socket

import org.py4grid.multicast.utils as mcast
from org.py4grid.multicast.daemons.DiscoverServers import Talker, Listener, ServerDaemon


class DiscoverDaemon(trd.Thread, Talker, Listener):

    MHOST = mcast.MCAST_DISCOVER
    MPORT = mcast.MCAST_DISCOVER_PORT

    def __init__(self, onlylisten=False):
        trd.Thread.__init__(self, daemon=True)
        Talker.__init__(self)

        self.onlylisten = onlylisten

        self.HostsRlock = multi.RLock()
        self.Hosts = []

        self.servers = ServerDaemon(onlylisten=True)
        self.servers.register_listener(self)
        self.servers.start()

        self.sock = mcast.getsocket(DiscoverDaemon.MHOST, DiscoverDaemon.MPORT)

        if not self.onlylisten:
            trd.Thread(target=DiscoverDaemon.discoverservers, args=(self,), daemon=True).start()

    def __del__(self):
        self.servers = None
        self.sock.stop()
        self.sock = None

    def listen(self, arg):
        with self.HostsRlock:
            hostname = arg.hostname
            hostip = socket.gethostbyname(hostname)
            adr = (hostip, arg.port)
            if not adr in self.Hosts:
                self.Hosts.append(adr)
                print('HOSTS UPDATE', self.Hosts)

    def gethosts(self):
        copy = []
        with self.HostsRlock:
            copy = self.Hosts[:]
        return copy

    def ProcessRequest(self):
        if not self.onlylisten:
            msg = mcast.Response()
            msg.pid = os.getpid()
            msg.ips = self.gethosts()
            self.sock.send(msg)

    @staticmethod
    def process(daemon, msg):
        if isinstance(msg, mcast.Request):
            daemon.ProcessRequest()
        elif isinstance(msg, mcast.Response):
            daemon.talk(msg)

    @staticmethod
    def discoverservers(daemon):
        while daemon.servers:
            daemon.servers.SendRequest()
            time.sleep(0.64)

    def sendrequest(self):
        try:
            msg = mcast.Request()
            self.sock.send(msg)
        except Exception as ex:
            raise

    def run(self):
        try:
            for msg in self.sock:
                trd.Thread(target=DiscoverDaemon.process, args=(self, msg), daemon=True).start()
        except Exception as ex:
            raise