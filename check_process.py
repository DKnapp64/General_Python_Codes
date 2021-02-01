import os
import sys

pid = str(os.getpid())
pidfile = "/tmp/mydaemon.pid"

if os.path.isfile(pidfile):
    print "%s already exists, exiting" % pidfile
    sys.exit()
else:
    file(pidfile, 'w').write(pid)

# Do some actual work here

os.unlink(pidfile)
