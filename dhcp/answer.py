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

#TFTP_SERVE_NAME_OPTION = ("TFTP_server_name", "192.168.56.1") # not needed.

def append_options(packet, options, append_end_option):
    if append_end_option:
        options.append(END_OPTION)

    for option in options:
        packet.options.append(
            Container(code=option[0],
                      value=Container(length=len(option[1]),
                                      data=option[1])))


def build_discover_answer(request_packet,
                          offer_boot=True,
                          ip_generator=generate_ip):
    # if not offer_boot and not GENERATE_IPS:
    #     return None # It will make client wait longer

    options = [
        SERVER_IDENTIFIER_OPTION,
        DHCP_TYPE_OFFER_OPTION
    ]

    if offer_boot:
        options.append(CLASS_IDENTIFIER_OPTION)
        options.append(BOOT_FILE_NAME_OPTION) # Required if GENERATE_IPS, but makes things faster anyway

    if GENERATE_IPS:
        options.append(SUBNET_MASK_OPTION)

    answer_packet = request_packet.copy()
    if GENERATE_IPS:
        client_ip = ip_generator()
        answer_packet.client_addr = client_ip
        answer_packet.your_addr = client_ip
        logger.info('Generated IP: %s' % client_ip)

    answer_packet.opcode = "BootReply"
    answer_packet.options = []
    append_options(answer_packet, options, True)
    return answer_packet


def create_ack(request_packet, offer_boot):
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

    options = [SERVER_IDENTIFIER_OPTION,
               DHCP_TYPE_ACK_OPTION]

    if offer_boot:
        options.extend([
               BOOT_FILE_NAME_OPTION,
               CLASS_IDENTIFIER_OPTION,
        ])

    append_options(ack_packet, options, True)

    logger.info('Sending ack')
    return ack_packet

