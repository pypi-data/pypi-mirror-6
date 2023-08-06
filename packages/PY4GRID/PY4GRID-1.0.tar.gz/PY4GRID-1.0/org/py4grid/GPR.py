import socket
import org.py4grid.GP as gp
import threading as trd
import socketserver


class HandleClient2(socketserver.BaseRequestHandler):

    def handle(self):
        ser = gp.Serializer(self.request)
        dic = ser.read()
        print('Process client...', self.client_address)
        print('Process function:', "'"+dic['function']+"'", 'on module:', "'"+dic['filename']+"'")
        ret = gp.ProcessRemoteWork(dic)
        ser.send(ret)


class HandleClient(trd.Thread):

    def __init__(self, conn):
        trd.Thread.__init__(self)
        self.conn = conn

    def run(self):
        try:

            ser = gp.Serializer(self.conn)
            dic = ser.read()
            ret = gp.ProcessRemoteWork(dic)
            ser.send(ret)

        except Exception as ex:
            raise exit
        finally:
            self.conn.close()


class Server(trd.Thread):

    def __init__(self, port):
        trd.Thread.__init__(self)
        self.port = port
        self._lock = trd.Lock()
        self._is_stop = True

    def stop_thread(self):
        with self._lock:
            self._is_stop = False

    def morework(self):
        ret = None
        with self._lock:
            ret = self._is_stop
        return ret

    def run(self):
        try:

            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('', self.port))
            self.server.listen(1)

            conn, addr = self.server.accept()
            cli = HandleClient(conn)
            cli.start()
            cli.join()

            self.server.close()

        except Exception as ex:
            raise ex
        finally:
            pass