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

import pickle
import socket
import struct
import io
import os


MAX_BYTES = 8192 * 2


def loads2(by):
    return pickle.load(io.BytesIO(initial_bytes=by))


def dumps2(obj):
    return pickle.dumps(obj)


class QuitRequest():

    def __init__(self):
        self.pid = os.getpid()

    def __repr__(self):
        return 'QuitRequest(pid=' + str(self.pid) + ')'


class Request():

    def __init__(self):
        self.pid = os.getpid()

    def __repr__(self):
        return 'Request(pid=' + str(self.pid) + ')'


class Response():

    def __init__(self, hostname=None, port=None, ips=()):
        self.pid = os.getpid()
        self.hostname = hostname
        self.port = port
        self.ips = ips

    def __repr__(self):
        return 'Response(pid=' + str(self.pid) + ', hostname=\'' + self.hostname + '\', ips=' + str(tuple(self.ips)) + ', port=' + str(self.port) + ')'


class MCastSocket():

    def __init__(self, mcasthost, mcastport):
        mreq = struct.pack("4sl", socket.inet_aton(mcasthost), socket.INADDR_ANY)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.adr = (mcasthost, mcastport)
        self.sock.bind(('', mcastport))

        self.is_continue = True

    def __del__(self):
        self.sock.close()
        self.sock = None

    def send(self, obj):
        data = dumps2(obj)
        if len(data) > MAX_BYTES:
            raise Exception('too large msg')
        self.sock.sendto(data, self.adr)

    def stop(self):
        self.is_continue = False

    def recv(self):
        data = self.sock.recv(MAX_BYTES)
        return loads2(data)

    def __iter__(self):
        return self

    def __next__(self):
        msg = self.recv()
        if not isinstance(msg, QuitRequest) and self.is_continue:
            return msg
        else:
            raise StopIteration



QUIT_MSG = (-1, -1)

MCAST_SERVERS = '224.1.1.1'
MCAST_DISCOVER = '224.1.2.1'

MCAST_SERVERS_PORT = 5007
MCAST_DISCOVER_PORT = 5700


def getsocket(host, port):
    sock = MCastSocket(host, port)
    return sock