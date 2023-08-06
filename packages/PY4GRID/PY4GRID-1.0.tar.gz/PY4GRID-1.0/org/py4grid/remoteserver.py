import sys


def main(init_args=None):
    dic = {'port': 4680, 'ip': ''}
    if init_args is None:
        init_args = sys.argv[1:]

    import org.py4grid.GPR as gpr
    import socketserver

    host = (dic['ip'], dic['port'])
    print('HOST', host)
    server = socketserver.TCPServer(host, gpr.HandleClient2)
    server.serve_forever()



if __name__ == '__main__':
    print(sys.argv)
    exit = main(init_args=sys.argv[1:])
    if exit:
        sys.exit(exit)