import logging
import socket

from dhcp_packet import dhcp_header, get_message_type, MESSAGE_TYPE_REQUEST, MESSAGE_TYPE_DISCOVER
from answer import build_discover_answer, create_ack
from udp_socket_listener import create_socket, serve

logger = logging.getLogger(__name__)

def default_boot_offer_filter(mac):
    return True

def dhcp_serve():
    def handler(s, addr, parsed_packet,
                ip_generator=None,
                boot_offer_filter=default_boot_offer_filter):
        message_type = get_message_type(parsed_packet)
        client_mac = parsed_packet.client_hardware_addr
        offer_boot = boot_offer_filter(client_mac)


        if message_type == MESSAGE_TYPE_DISCOVER:

            if not offer_boot: # it's here, so it wont be logged many times.
                logger.info("Not booting client: %s" % client_mac)

            if ip_generator:
                response = build_discover_answer(parsed_packet,
                                                 ip_generator,
                                                 offer_boot)
            else:
                response = build_discover_answer(parsed_packet,
                                                 offer_boot)
            if response:
                logger.info('Answering Discover')

        elif message_type == MESSAGE_TYPE_REQUEST:
            response = create_ack(parsed_packet,
                                  offer_boot)
            if response:
                    logger.info('Answering Request')
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