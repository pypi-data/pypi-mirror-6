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

import pickle
import socket
import platform
import math
import threading
import os as os
import platform as pt
import sys
import time

from multiprocessing.pool import Pool as Pool

from org.py4grid.multicast.daemons.DiscoverDaemons import DiscoverDaemon
from org.py4grid.multicast.daemons.DiscoverServers import Listener


def rmrecursive(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)


def ProcessRemoteWork(dic):

    func_name = dic['function']
    func_filename = dic['filename']
    func_args = dic['args']

    part = list(os.path.split(func_filename))

    relative = dic['relative_path']

    if pt.system() in relative.keys():
        part[0] = relative[pt.system()]
    part = tuple(part)

    old = os.getcwd()
    os.chdir(part[0])

    py_module = part[1][:-3]
    cmd = 'from ' + py_module + ' import ' + func_name + ' as function'

    sys.path.insert(0, part[0])

    exec(cmd, globals(), locals())

    func_name = locals()['function']

    pool = Pool()
    ret = pool.map(func_name, func_args)

    pool.close()
    pool.join()

    pycache = os.path.join(part[0], '__pycache__')
    rmrecursive(pycache)

    del sys.path[0]
    del sys.modules[py_module]
    del locals()['function']

    print('PATH', tuple(sys.path))
    print('LOADED MODULES', tuple(sys.modules.keys()))
    print('GLOBALS', tuple(globals().keys()))
    print('LOCALS', tuple(locals().keys()))

    os.chdir(old)

    return tuple(ret)


class Serializer():

    def __init__(self, sock):
        self.sock = sock

    def send(self, obj):
        file = self.sock.makefile(mode='wb')
        pickle.dump(obj, file)
        file.close()

    def read(self):
        file = self.sock.makefile(mode='rb')
        ret = pickle.load(file)
        file.close()
        return ret


class Partitioner():

    def __init__(self, iterable):
        self.iterable = iterable

    def part(self, parts):

        def part2(seq, max):
            return [tuple(seq[x:x+max]) for x in range(0, len(seq), max)]

        return part2(self.iterable, parts)


def process_one(tp):

    rec = None

    try:
        dic = tp[0]
        host = tp[1]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        HOST = host[0]
        PORT = host[1]

        sock.connect((HOST, PORT))

        ser = Serializer(sock)
        ser.send(dic)
        rec = ser.read()
        sock.close()
    except Exception as ex:
        return [ex]
    finally:
        pass
    return rec


def process_alone(item):
    dic = item[0]
    return ProcessRemoteWork(dic)


def regroup(iterable):
    tmp = []
    for item in iterable:
        tmp.extend(item)
    return tmp


class RemoteProcess(Listener):

    def __init__(self, pool, file=None, discover_hosts=False):
        self.pool = pool
        self.__new_file__ = file
        self.bool_discover = discover_hosts

        self.discover_hosts = []
        self.discover_rlock = threading.RLock()
        self.discover = DiscoverDaemon(onlylisten=True)
        self.discover.register_listener(self)
        self.discover.start()
        self.discover.sendrequest()

    def stop(self):
        self.discover = None

    def listen(self, arg):
        with self.discover_rlock:
            print('RECV HOTS ADDR', arg.ips)
            self.discover_hosts.clear()
            self.discover_hosts.extend(arg.ips)

    def gethosts(self):
        copy = []
        copy.clear()
        with self.discover_rlock:
            copy = self.discover_hosts[:]
        return copy

    def processwork(self, filename, func=None, iterable=(), relative_path={}, hosts=()):

        iterable = tuple(iterable)

        relative_path[platform.system()] = os.path.split(filename)[0]

        part = Partitioner(iterable)

        dic = {'function': func.__name__, 'filename': filename, 'relative_path': relative_path}

        dictionaries = tuple([dic] * len(hosts))
        host_args = zip(dictionaries, hosts)
        func = None

        if self.bool_discover:
            self.discover.sendrequest()
            time.sleep(0.01)
            tmp = self.gethosts()
            print('TMP', tmp)
            if len(hosts) == 0:
                hosts = tmp

        if len(hosts) == 0:
            part = part.part(len(iterable))
            hosts = (('', 0),)
            func = process_alone
        else:
            part = part.part(math.ceil(len(iterable)/len(hosts)))
            func = process_one

        dictionaries = tuple([dic] * len(hosts))
        host_args = zip(dictionaries, hosts)

        args = []
        for i, item in enumerate(host_args):
            print(i, item)
            item[0]['args'] = part[i]
            args.append(item)
        args = tuple(args)
        host_args = args

        print('HOSTS', hosts)
        print('FUNC', func)
        print('HOST_ARGS', host_args)

        pool = self.pool()
        result = pool.map(func, host_args)
        pool.close()
        pool.join()

        result = regroup(result)

        return tuple(result)