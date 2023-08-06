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

import threading as trd
import socketserver

import org.py4grid.GP as gp


class HandleClient2(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            ser = gp.Serializer(self.request)
            dic = ser.read()
            print('Process client...', self.client_address)
            print('Process function:', "'"+dic['function']+"'", 'on module:', "'"+dic['filename']+"'")
            ret = gp.ProcessRemoteWork(dic)
            ser.send(ret)
        except EOFError as eof:
            print('EOFError', ':', eof, ':', 'Final de arquivo encontrado...')
        except Exception as ex:
            raise


class Server(trd.Thread):

    def __init__(self, port):
        trd.Thread.__init__(self)
        self.port = port
        self._lock = trd.Lock()
        self._is_stop = True
        self.cause = None
        self.pool = socketserver.TCPServer(('', self.port), HandleClient2)

    def stop_thread(self):
        with self._lock:
            self._is_stop = False
            #self.server.close()
            self.pool.shutdown()

    def morework(self):
        ret = None
        with self._lock:
            ret = self._is_stop
        return ret

    def run(self):
        try:
            self.pool.serve_forever()
            '''
            while self.morework():

                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind(('', self.port))
                self.server.listen(1)

                conn, addr = self.server.accept()
                cli = HandleClient(conn)
                cli.start()
                cli.join()

            self.server.close()
            '''

        except OSError as ose:
            if ose.args[0] == 10004:
                self.cause = ose.args[1]
        except Exception as ex:
            raise ex
        finally:
            #self.server.close()
            pass