BOOT_FILES_DIR = 'kpypxe'
BOOT_FILE_NAME = 'lpxelinux.0'

TFTP_SERVE_DIR = r'C:\temp\tftp'
TFTP_MENUS_DIR = r'C:\temp\tftp\pxelinux.cfg'
DEFAULT_BOOT_MENU = 'default'

SERVER_IP = '192.168.56.1' # or socket.gethostbyname(socket.gethostname())

# This is not a good DHCP server for real networks!
GENERATE_IPS = False
IPS_START = '192.168.56.2'
IPS_END   = '192.168.56.199'
SUBNET_MASK = "255.255.255.0"
