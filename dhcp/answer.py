import logging
from construct import Container

from config import BOOT_FILES_DIR, BOOT_FILE_NAME, SERVER_IP, SUBNET_MASK, GENERATE_IPS
from dhcp.dhcp_packet import MESSAGE_TYPE_OFFER, MESSAGE_TYPE_ACK, IpAddress
from dhcp.stupid_ip_generator import generate_ip

logger = logging.getLogger(__name__)

_IP_BIN = IpAddress(None).build

# dhcp options: (name, value)
END_OPTION = ("End", "")
SERVER_IDENTIFIER_OPTION = ("Server_identifier", _IP_BIN(SERVER_IP))
CLASS_IDENTIFIER_OPTION = ("Class_identifier", "PXE Client")
BOOT_FILE_NAME_OPTION = ("Bootfile_name",
                         BOOT_FILES_DIR + '/' + BOOT_FILE_NAME)

DHCP_TYPE_OFFER_OPTION = ("DHCP_message_type", MESSAGE_TYPE_OFFER)
DHCP_TYPE_ACK_OPTION = ("DHCP_message_type", MESSAGE_TYPE_ACK)

SUBNET_MASK_OPTION = ("Subnet_Mask", _IP_BIN(SUBNET_MASK))

# ("TFTP_server_name", "192.168.56.1") not needed.

def append_options(packet, options):
    for option in options:
        packet.options.append(
            Container(code=option[0],
                      value=Container(length=len(option[1]),
                                      data=option[1])))


def build_discover_answer(request_packet,
                          ip_generator=generate_ip,
                          options_addon=None):
    options = [
        SERVER_IDENTIFIER_OPTION,
        CLASS_IDENTIFIER_OPTION,
        DHCP_TYPE_OFFER_OPTION
    ]
    if GENERATE_IPS:
        options.append(SUBNET_MASK_OPTION)
    if options_addon:
        options.extend(options_addon)
    options.append(END_OPTION)

    answer_packet = request_packet.copy()
    if GENERATE_IPS:
        client_ip = ip_generator()
        answer_packet.client_addr = client_ip
        answer_packet.your_addr = client_ip
        logger.info('Generated IP: %s' % client_ip)

    answer_packet.opcode = "BootReply"
    answer_packet.options = []
    append_options(answer_packet, options)
    logger.info('Answering Discover')
    return answer_packet


def create_ack(request_packet):
    def get_option(code, default):
        for option in request_packet.options:
            if code == option.code:
                return option.value.data
        return default
    if not GENERATE_IPS and request_packet.flags.boardcast:
        return
    ack_packet = request_packet.copy()
    ack_packet.opcode = "BootReply"

    if GENERATE_IPS:
        client_ip = get_option('Requested_IP_Address', _IP_BIN('0.0.0.0'))
        ack_packet.your_addr = client_ip
    else:
        client_ip = request_packet.client_addr

    ack_packet.client_addr = _IP_BIN(client_ip)
    ack_packet.server_addr = _IP_BIN(SERVER_IP)
    ack_packet.options = []
    for option in ack_packet.options:
        if option.code == 'DHCP_message_type':
            option.value.data = MESSAGE_TYPE_ACK
    options = [SERVER_IDENTIFIER_OPTION,
               CLASS_IDENTIFIER_OPTION,
               DHCP_TYPE_ACK_OPTION,
               BOOT_FILE_NAME_OPTION,
               END_OPTION]
    append_options(ack_packet, options)
    # ack_packet.options = [option for option in ack_packet.options if \
    #                      option.code not in ('User_Class_Information',
    #                                          'Parameter_request_list',
    #                                          'Requested_IP_Address')]
    logger.info('Sending ack')
    return ack_packet

