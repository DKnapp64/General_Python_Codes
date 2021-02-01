#!/usr/bin/env python

import sys, os, time, atexit
from signal import SIGTERM 
from ftplib import FTP
import subprocess
import re
from datetime import timedelta, datetime, tzinfo

class Daemon:
	"""
	A generic daemon class.
	
	Usage: subclass the Daemon class and override the run() method
	"""
	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/stdout', stderr='/dev/stderr'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
	
	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)

                while True:
                  now = datetime.utcnow()
                  while (now < datetime(now.year, now.month, now.day, 23, 0, 0)):
                    checktime = 0
                    while (checktime == 0):
                      now = time.gmtime() 
                      time.sleep(30.0)
                      if (now.tm_min == 37 or now.tm_min == 7):
 	               print("Minutes are 37 or 7")
                       checktime = 1
 
                  print("Past While loop")
                  checktime = 0
                  os.chdir('/shared/Labs/Asner/Private/Research/Researcher/Knapp/GOES')
                  try:
                    ftp = FTP('satepsanone.nesdis.noaa.gov')
                  except (socket.error, socket.gaierror), e:
                    print 'ERROR: cannot reach satepsanone.nesdis.noaa.gov'
                  print '*** Connected to host satepsanone.nesdis.noaa.gov'
   
                  ftp.login()
                  ftp.cwd('GIS/GOESeast')
                  filelist = ftp.nlst()
   
                  tiflist = []
                  sizelist = []
                  ## find the last and latest file
                  for element in filelist:
                    if re.search("tif", element):
                      tiflist.append(element)
                      sizelist.append(ftp.size(element))
   
                  if (sizelist[-1] != sizelist[-2]):
                    latesttif = tiflist[-3]
                  else:
                    latesttif = tiflist[-2]
   
                  fhandle = open(latesttif, 'wb')
                  ftp.retrbinary('RETR '+latesttif, fhandle.write)
                  fhandle.close()   # not sure if this is needed
                  ftp.quit()
   
                  now = time.gmtime()
                  mod15time = (now.tm_min // 15) * 15
                  if ((mod15time % 30) == 0):
                    mod15time = mod15time - 15
   
                  nowfile = ('%s%03d%02d%02d%s') % ('GoesEast1V', now.tm_yday, now.tm_hour, mod15time, '.tif')
                  print 'NOW file is: %s' % (nowfile)
                  nowsize = ftp.size(nowfile)
                  kmlname = (os.path.splitext(nowfile))[0] + "_KML.kmz"
                  print 'NOW file is: %s and %d bytes' % (nowfile, nowsize)
                  ## see if the file is in the list   
                  indexval = filelist.index(nowfile)
                  if (nowfile in filelist):
                    if ((os.path.isfile(nowfile) == False) and (ftp.size(nowfile) > 2000)):
                      fhandle = open(nowfile, 'wb')
                      ftp.retrbinary('RETR '+nowfile, fhandle.write)
                      fhandle.close()   # not sure if this is needed
                    ftp.quit()
                  subprocess.call(["gdal_translate", "-of", "KMLSUPEROVERLAY", "-projwin", "-82.0", "2.0", "-75.0", "-6.0", nowfile, kmlname, "-co", "FORMAT=JPEG"]) 

	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if pid:
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print str(err)
				sys.exit(1)

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()

	def run(self):
		"""
		You should override this method when you subclass Daemon. It will be called after the process has been
		daemonized by start() or restart().
		"""
