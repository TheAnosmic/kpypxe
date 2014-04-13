from threading import Thread
import logging

from dhcp.listener import dhcp_serve
from tftp.listener import tftp_serve

if '__main__' == __name__:
    logging.basicConfig(level=logging.INFO)
    Thread(target=dhcp_serve).start()
    Thread(target=tftp_serve).start()
    raw_input('Running...\n')
