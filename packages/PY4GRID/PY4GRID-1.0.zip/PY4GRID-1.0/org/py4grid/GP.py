import pickle
import socket
import platform
import math
from multiprocessing.pool import Pool
import os as os
import platform as pt
import sys


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
    cmd = 'from ' + py_module + ' import ' + func_name + ' as funcao'

    sys.path.insert(0, part[0])

    exec(cmd, globals(), locals())

    func_name = locals()['funcao']

    pool = Pool()
    ret = pool.map(func_name, func_args)

    pool.close()
    pool.join()

    pycache = os.path.join(part[0], '__pycache__')
    rmrecursive(pycache)


    del sys.path[0]
    del sys.modules[py_module]
    del locals()['funcao']

    print('PATH', sys.path)
    print('LOADED MODULES', sys.modules.keys())
    print('GLOBALS', globals().keys())
    print('LOCALS', locals().keys())

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

    dic = tp[0]
    host = tp[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HOST = host[0]
    PORT = host[1]

    sock.connect((HOST, PORT))

    print('SOCK', sock)

    ser = Serializer(sock)
    ser.send(dic)
    rec = ser.read()
    sock.close()

    return rec


def process_alone(item):
    dic = item[0]
    return ProcessRemoteWork(dic)


class RemoteProcess():

    def __init__(self, pool, file=None):
        self.pool = pool
        self.__new_file__ = file

    def processwork(self, filename, func=None, iterable=(), relative_path={}, hosts=()):

        iterable = tuple(iterable)

        relative_path[platform.system()] = os.path.split(filename)[0]

        result = []
        part = Partitioner(iterable)

        dic = {'function': func.__name__, 'filename': filename, 'relative_path': relative_path}

        dictionaries = tuple([dic] * len(hosts))
        host_args = zip(dictionaries, hosts)
        func = None

        pool = self.pool()

        if len(hosts) == 0:
            part = part.part(len(iterable))
            hosts = (('', 0),)
            dictionaries = tuple([dic] * len(hosts))
            host_args = zip(dictionaries, hosts)
            func = process_alone
        else:
            part = part.part(math.ceil(len(iterable)/len(hosts)))
            func = process_one

        args = []
        for i, item in enumerate(host_args):
            item[0]['args'] = part[i]
            args.append(item)
        args = tuple(args)
        host_args = args

        result = pool.map(func, host_args)
        pool.close()
        pool.join()

        return tuple(result)


class MultimachinePool(Pool):

    def __init__(self, processes=None, initializer=None, initargs=(), maxtasksperchild=None):
        Pool.__init__(self, processes=processes, initializer=initializer,initargs=initargs,maxtasksperchild=maxtasksperchild)

    def map(self, func, iterable, chunksize=None):
        Pool.map(self, func, iterable, chunksize)