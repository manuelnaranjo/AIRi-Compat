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
