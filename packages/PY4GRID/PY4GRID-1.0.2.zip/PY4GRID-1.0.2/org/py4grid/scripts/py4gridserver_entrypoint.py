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

import argparse
import socketserver
import sys
import os

MODEL_BASE = None
if hasattr(os, 'fork'):
    MODEL_BASE = socketserver.ForkingTCPServer
else:
    MODEL_BASE = socketserver.ThreadingTCPServer
    MODEL_BASE.daemon_threads = True


def main(init_args=None):

    import org.py4grid.GPR as gpr
    import org.py4grid.multicast.daemons.DiscoverServers as discover

    discover_server = None
    server = None
    server_thread = None

    parse = argparse.ArgumentParser(prog='PY4GRIDSERVER')
    parse.add_argument('-port', help='a port to server usage to listen, default is 4680', default=4680, type=int)

    init_args = parse.parse_args(init_args)

    try:
        dic = {'port': init_args.port, 'ip': ''}

        host = (dic['ip'], init_args.port)
        print('HOST', host)

        server = MODEL_BASE(host, gpr.HandleClient2)

        discover_server = discover.ServerDaemon(port=init_args.port)

        discover_server.start()

        print('SERVER_ADDRESS', server.server_address)
        server.serve_forever()

    except KeyboardInterrupt as kex:
        print('KEYBOARD interrupt...')
    except Exception as ex:
        print('Exception :', ex, '...')
    finally:
        print('Closing server...')
        sys.exit(0)


if __name__ == '__main__':
    print(sys.argv)
    main(init_args=sys.argv[1:])
    sys.exit(0)