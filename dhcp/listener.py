import socket

from dhcp_packet import dhcp_header, get_message_type, MESSAGE_TYPE_REQUEST, MESSAGE_TYPE_DISCOVER
from answer import build_discover_answer, create_ack
from udp_socket_listener import create_socket, serve


def dhcp_serve():
    def handler(s, addr, parsed_packet, ip_generator=None):
        message_type = get_message_type(parsed_packet)
        if message_type == MESSAGE_TYPE_DISCOVER:
            if ip_generator:
                response = build_discover_answer(parsed_packet,
                                                 ip_generator)
            else:
                response = build_discover_answer(parsed_packet)
        elif message_type == MESSAGE_TYPE_REQUEST:
            response = create_ack(parsed_packet)
        else:
            return
        if not response:
            return
        built_answer = dhcp_header.build(response)

        if '0.0.0.0' == addr[0]:
            target = '<broadcast>', addr[1]
        else:
            target = addr
        s.sendto(built_answer, target)

    def filter_func(parsed_packet):
        return True

    import threading
    threading.Thread(target=serve,
                     args=(67, handler,
                           dhcp_header.parse,
                           filter_func)).start()
    # Both ports need to answer, something with handovering the
    # pxe responsibility from the real dhcp.
    serve(4011, handler, dhcp_header.parse, filter_func)

if '__main__' == __name__:
    dhcp_serve()