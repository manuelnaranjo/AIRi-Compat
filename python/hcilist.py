import bluetooth, struct
from ioctl import ioctl
from bluetooth._bluetooth import *
import ctypes

HCI_MAX_DEV=16

class hci_dev_req(ctypes.Structure):
    _fields_=[
        ("dev_id",  ctypes.c_uint16),
        ("dev_opt", ctypes.c_uint32)
    ]
hci_dev_req_p=ctypes.POINTER(hci_dev_req)

class hci_dev_list_req(ctypes.Structure):
    _fields_=[
        ("dev_num", ctypes.c_uint16),
        ("dev_req", hci_dev_req*HCI_MAX_DEV)
    ]
hci_dev_list_p=ctypes.POINTER(hci_dev_list_req)
    
class bdaddr_t(ctypes.Structure):
    _fields_ = [
        ("b",   ctypes.c_uint8*6)
    ]
    
    def __str__(self):
        return ":".join(["%02X" % x for x in reversed(self.b)])

class hci_dev_stats(ctypes.Structure):
    _fields_ = [
        ("err_rx",  ctypes.c_uint32),
        ("err_tx",  ctypes.c_uint32),
        ("cmd_tx",  ctypes.c_uint32),
        ("evt_rx",  ctypes.c_uint32),
        ("acl_tx",  ctypes.c_uint32),
        ("acl_rx",  ctypes.c_uint32),
        ("sco_tx",  ctypes.c_uint32),
        ("sco_rx",  ctypes.c_uint32),
        ("byte_rx",  ctypes.c_uint32),
        ("byte_tx",  ctypes.c_uint32),
    ]

class hci_dev_info(ctypes.Structure):
    _fields_ = [
        ("dev_id",      ctypes.c_uint16),
        ("name",        ctypes.c_char*8),
        ("bdaddr",      bdaddr_t),
        ("flags",       ctypes.c_uint32),
        ("type",        ctypes.c_uint8),
        ("features",    ctypes.c_uint8*8),
        ("pkt_type",    ctypes.c_uint32),
        ("link_policy", ctypes.c_uint32),
        ("link_mode",   ctypes.c_uint32),
        ("acl_mtu",     ctypes.c_uint16),
        ("acl_pkts",    ctypes.c_uint16),
        ("sco_mtu",     ctypes.c_uint16),
        ("sco_pkts",    ctypes.c_uint16),
        ("stat",        hci_dev_stats),
   ]
hci_dev_info_p=ctypes.POINTER(hci_dev_info)

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

FLAGS={
    0: "UP",
    1: "INIT",
    2: "RUNNING",
    3: "PSCAN",
    4: "ISCAN",
    5: "AUTH",
    6: "ENCRYPT",
    7: "INQUIRY",
    8: "RAW"
}
def flags_to_str(flags):
    out=[]
    
    if not flags & 0x01:
        out.append("DOWN")
    for f in FLAGS:
        if flags & 1 << f:
            out.append(FLAGS[f])
    return " ".join(out)

TYPES={
    0: "BD/EDR",
    1: "AMP"
}

BUS={
    0: "VIRTUAL",
    1: "USB",
    2: "PCCARD",
    3: "UART",
    4: "RS232",
    5: "PCI",
    6: "SDIO"
}

if __name__=='__main__':
    FORMAT="id: %02i internal: %s\naddr: %s type: %s bus: %s\nflags: %s"
    for dev in devs().itervalues():
        print FORMAT % (dev.dev_id, dev.name, dev.bdaddr, 
            TYPES.get(dev.type >> 4, "INVALID"), 
            BUS.get(dev.type & 0x0f, "INVALID"), 
            flags_to_str(dev.flags))
        bluetooth._bluetooth.hci_open_dev(dev.dev_id)
