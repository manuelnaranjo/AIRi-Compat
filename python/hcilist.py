import bluetooth, struct
from ioctl import ioctl
from bluetooth._bluetooth import *
import ctypes

from hcilib import *

def devs():
    buf=hci_dev_list_req()
    buf.dev_num=HCI_MAX_DEV
    ctl = bluetooth.BluetoothSocket(proto=bluetooth.HCI)
    ret=ioctl(ctl.fileno(), HCIGETDEVLIST, hci_dev_list_p(buf))
    if ret < 0 :
        raise Exception("something failed")
    out = {}
    for i in range(buf.dev_num):
        dev_req = buf.dev_req[i]
        dev = hci_dev_info()
        dev.dev_id = dev_req.dev_id
        ret = ioctl(ctl.fileno(), HCIGETDEVINFO, hci_dev_info_p(dev))
        out[dev.dev_id] = dev
    return out

if __name__=='__main__':
    FORMAT="id: %02i internal: %s\naddr: %s type: %s bus: %s\nflags: %s"
    for dev in devs().itervalues():
        print FORMAT % (dev.dev_id, dev.name, dev.bdaddr, 
            TYPES.get(dev.type >> 4, "INVALID"), 
            BUS.get(dev.type & 0x0f, "INVALID"), 
            flags_to_str(dev.flags))
        bluetooth._bluetooth.hci_open_dev(dev.dev_id)
