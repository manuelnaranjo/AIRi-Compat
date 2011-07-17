from ctypes import *

try:
    libc = CDLL ('libc.so.6', use_errno=True)
    if not hasattr(libc, "ioctl"):
        raise Exception("No ioctl")
except:
    # happens on Android
    libc = CDLL ('libc.so', use_errno=True)
    if not hasattr(libc, "ioctl"):
        raise Exception("No ioctl")
#print libc.ioctl

libc.ioctl.argtypes = (c_int, c_int, c_void_p)

_IOC_WRITE = 0x1

_IOC_NRBITS=    8
_IOC_TYPEBITS=  8
_IOC_SIZEBITS=  14
_IOC_DIRBITS=   2

_IOC_NRSHIFT=   0
_IOC_TYPESHIFT= (_IOC_NRSHIFT+_IOC_NRBITS)
_IOC_SIZESHIFT= (_IOC_TYPESHIFT+_IOC_TYPEBITS)
_IOC_DIRSHIFT=  (_IOC_SIZESHIFT+_IOC_SIZEBITS)


def _IOC (dir, type, nr, size):
    return (((dir)  << _IOC_DIRSHIFT) | \
         ((type) << _IOC_TYPESHIFT) | \
         ((nr)   << _IOC_NRSHIFT) | \
         ((size) << _IOC_SIZESHIFT))

def ioctl (fd, request, args):
    return libc.ioctl (fd, request, args)
