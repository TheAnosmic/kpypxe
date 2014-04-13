from config import IPS_START, IPS_END
from random import randint

# for playing around only.
def generate_ip():
    ip = []
    for start, end in zip(
            IPS_START.split('.'),
            IPS_END.split('.')):
        if start == end:
            ip.append(start)
        else:
            ip.append(str(randint(
                int(start), int(end))))
    return '.'.join(ip)

if '__main__' == __name__:
    for i in range(5):
        print generate_ip()