import android, time, os, traceback
droid = android.API()
dumpp = droid.environment()["download"]
os.system("mkdir -p %s" % dumpp)
dumpf = os.path.join(dumpp, "AIRi-compat-%s.log" % int(time.time()))
droid.makeToast('Dumping results to %s' % dumpf)

try:
    dump = open(dumpf, "w")
except Exception, err: 
    droid.log(repr(err))


def dump_line(content):
    droid.log(repr(content))
    dump.write(content+"\n")
    dump.flush()

def dump_error(err):
    dump_line("ERROR: " + repr(err))
    traceback.print_exc(file=dump)

def dump_lines(content):
    for l in content.splitlines(): 
        dump_line(l)


dump_line("Starting tests %s" % dumpf)

dump_line("uname")
dump_line(os.popen("uname -a").read())

dump_line("Mounted partitions")
dump_lines(os.popen("mount").read())

dump_line("Checking sysfs")
try:
    sysfs = os.popen("mount | grep sysfs").readlines()[0].split()[2]
except Exception, err:
    dump_error(err)
    sysfs = None

try:
    dump_line("Environment")
    dump_lines(os.popen("/system/bin/toolbox printenv").read())
    dump_line("Properties")
    dump_lines(os.popen("/system/bin/toolbox getprop").read())    
    dump_line("Kernel modules")
    dump_lines(os.popen("/system/bin/toolbox lsmod").read())
    dump_line("netstat")
    dump_lines(os.popen("/system/bin/toolbox netstat").read())
    dump_line("Mounted partitions")
    dump_lines(os.popen("/system/bin/toolbox mount").read())
except Exception, err:
    dump_error(err)

dump_line("------------------------------------------------")

try:
    dump_line("files in / %s" % os.listdir("/"))
    dump_line("files in /proc %s" % os.listdir("/proc"))
    dump_line("files in /sys %s" % os.listdir("/sys"))     
except Exception, err:
    dump_error(err)

dump_line("------------------------------------------------")
dump_line("Checking procfs")    
try:
    procfs = os.popen("mount | grep proc").readlines()[0].split()[2]
except Exception, err:
    dump_error(err)
    procfs = None

if procfs:
    try:
        dump_line("k version %s" % open("%s/version" % procfs).read())
    except Exception, err:
        dump_error(err)

if sysfs:
    dump_line("sysfs: %s" %sysfs)
    dump_line("modules")
    for k in os.listdir("%s/module" % sysfs):
        dump_line(k)

if procfs:
    dump_line("procfs: %s" % procfs)
    for k in os.listdir("%s" % procfs):
        dump_line(k)
dump_line("------------------------------------------------")

def process_list():
    dump_line("------------------------------------------------")
    dump_line("Process list")
    dump_lines(os.popen("ps").read())
    dump_lines(os.popen("/system/bin/toolbox ps").read())

def test_kernel():
    pass


def test_bluez():
    dump_line("------------------------------------------------")
    import hcilist, bluetooth
    FORMAT="id: %02i internal: %s\naddr: %s type: %s bus: %s\nflags: %s"
    for dev in hcilist.devs().itervalues():
        dump_line(FORMAT % (dev.dev_id, dev.name, dev.bdaddr, 
            hcilist.TYPES.get(dev.type >> 4, "INVALID"), 
            hcilist.BUS.get(dev.type & 0x0f, "INVALID"), 
            hcilist.flags_to_str(dev.flags)))
        try:
            bluetooth._bluetooth.hci_open_dev(dev.dev_id)
        except Exception, err:
            dump_error(err)

    dump_line("dev id %s" % bluetooth._bluetooth.hci_devid())
    dump_line("------------------------------------------------")
    try:
        import ctypes
        bt=ctypes.CDLL("libbluetooth.so")
        dump_line("%s" % bt)
        r = bt.hci_get_route(0)
        dump_line("hci_get_route %s" % r)
        dump_line("%s" % bt.hci_open_dev(r))
    except Exception, err:
        dump_error(err)

def test_android_api():
    dump_line("------------------------------------------------")
    def scanAndSelect():
        droid.makeToast("Please wait while scanning the air")
        dump_line("scanning")
        devices = droid.bluetoothScan()
        for dev in devices:
            dump_line("%s" % dev)
        droid.dialogCreateInput("AIRi Compat", "Please choose one device")
        for dev in devices:
            dev["bonded_string"] = "bonded" if dev["bonded"] else ""
        droid.dialogSetItems(["%(address)s: %(name)s %(bonded_string)s"%d for d in devices])
        droid.dialogShow()
        res=droid.dialogGetResponse()
        if "item" in res:
            return devices[res["item"]]["address"]
        return None
            
    def test_connection(method, address, channel):
        dump_line("testing %s on channel %s" %(address, channel))
        method = droid.__getattr__(method) 
        dump_line("result: %s" % method(address, channel)) 
        dump_line("read: %s" % droid.myBluetoothRead())
        dump_line("disconnecting %s" % droid.myBluetoothDisconnect())

    dev = None
    while dev == None:
        dev = scanAndSelect()
        if dev: break
        droid.makeToast("You need to choose a device!!!")
        time.sleep(5)
        
    dump_line("testing with %s" % dev) 
    test_connection("myBluetoothConnectRfcomm", dev, 1)
    test_connection("myBluetoothConnectL2CAP", dev, 0x1001)
    
TESTS=[process_list, test_kernel, test_bluez, test_android_api]

for test in TESTS:
    try:
        dump_line("Running: %s" % repr(test))
        test()
    except Exception, err:
        droid.makeToast(repr(test) + " failed!")
        dump.write(str(err))
        traceback.print_exc(file=dump)

droid.makeToast("Done")
dump.close()
droid.sendEmail("manuel@aircable.net", "AIRi Compat Result Tests", "ATTACHED",
    "file://%s" % dumpf)
