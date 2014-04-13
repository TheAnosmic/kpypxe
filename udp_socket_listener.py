import socket


def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('0.0.0.0', port))
    return s

def serve(port,
          handler,
          parser=None,
          filter_func=None):
    s = create_socket(port)
    while True:
        try:
            message, address = s.recvfrom(8192)
            if parser:
                packet = parser(message)
            else:
                packet = message
            if filter_func and not filter_func(packet):
                continue
            handler(s, address, packet)
        except KeyboardInterrupt:
            exit()