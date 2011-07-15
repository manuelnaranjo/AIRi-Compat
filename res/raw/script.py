import android, time, os, traceback
droid = android.Android()
dumpp = droid.environment().result["download"]
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

def process_list():
    dump_line("Process list")
    dump_lines(os.popen("ps -ef").read())

def test_kernel():
    pass


def test_bluez():
    import bluetooth
    dump.write("dev id %s" % bluetooth._bluetooth.hci_devid())

TESTS=[process_list, test_kernel, test_bluez,]

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
