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

import sys
import threading
import signal
import time


def main(init_args=None):

    import org.py4grid.multicast.daemons.DiscoverDaemons as dv

    if init_args is None:
        init_args = sys.argv[1:]

    server = None

    try:

        server = dv.DiscoverDaemon()
        server.start()

        server.join()

    except KeyboardInterrupt as kex:
        print('KEYBOARD interrupt...')
    finally:
        print('Closing server...')
        sys.exit(0)


if __name__ == '__main__':
    print(sys.argv)
    main(init_args=sys.argv[1:])
    sys.exit(0)
