import logging
import os

from construct import Container

from tftp.tftp_client_session import TFTPClientSession
from tftp.tftp_packet import tftp_header
from udp_socket_listener import serve
from config import BOOT_FILES_DIR, TFTP_SERVE_DIR, TFTP_MENUS_DIR, DEFAULT_BOOT_MENU


SESSIONS = {}

PXE_LINUX_CONF_DIR = 'pxelinux.cfg'

logger = logging.getLogger(__name__)

def get_menu_file(request):
    return os.path.join(TFTP_MENUS_DIR, DEFAULT_BOOT_MENU)


def get_file_to_serve(request,
                      menu_file_handler=get_menu_file):
    if not request.startswith(BOOT_FILES_DIR):
        return  # Not my job

    request = request.replace(BOOT_FILES_DIR + '/', '', 1)

    if PXE_LINUX_CONF_DIR in request:
        request = request.replace(PXE_LINUX_CONF_DIR + '/', '', 1)
        requested_file = menu_file_handler(request)
    else:
        requested_file = os.path.join(TFTP_SERVE_DIR, *request.split('/'))

    return requested_file if os.path.exists(requested_file) else None


def tftp_serve(menu_file_handler=None):
    def handler(s, addr, packet):
        def get_option(name, default):
            """
            extracting the value of the option {name}
            from tftp packet.
            """
            for option in packet.options:
                if option.name == name:
                    return option.value
            return default

        def send(built_answer):
            s.sendto(built_answer, addr)

        if packet.opcode == 'READ_REQ':
            logger.info('requested: %s' % packet.source_file)
            if menu_file_handler:
                file_to_return = get_file_to_serve(packet.source_file, menu_file_handler)
            else:
                file_to_return = get_file_to_serve(packet.source_file)

            if not file_to_return or not os.path.exists(file_to_return):
                logger.error('requested file not exists: %s' % file_to_return)
                return
            logger.info('served: %s' % file_to_return)

            blksize = int(get_option('blksize', 512))
            stream = open(file_to_return, 'rb')
            SESSIONS[addr] = TFTPClientSession(stream, blksize)

            if blksize != 512: # need to ack the block size
                answer = Container(opcode='OACK', options=[
                    Container(value=str(blksize), name='blksize')])
                send(tftp_header.build(answer))
                return

        session = SESSIONS[addr]

        answer = Container(
            opcode='DATA_PACKET',
            options=[]
        )
        if packet.opcode == 'ACK':
            answer.block = packet.block + 1
        else:
            answer.block = 0

        block = session.get_block(answer.block)

        if not block:
            session.close()
            return

        built_answer = tftp_header.build(answer)
        built_answer += block
        send(built_answer)

    serve(69, handler, tftp_header.parse)


if '__main__' == __name__:
    logging.basicConfig(level=logging.INFO)
    tftp_serve()