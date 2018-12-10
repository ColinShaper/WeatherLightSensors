##############################################################
# LogWrite.py
# Colin Shaper
# ver 2018-12-10 cleanup comments
# Colin Shaper, all rights reserved, 2010-2018
##############################################################
# subroutines
# logwrite sends the supplied message to a log comprising
#  the passed program name and a datestamp. Log is written
#  to the 'current' directory. A newline is added to the
#  message and the log is opened and closed for each log
#  message
#  This is typically used for temporary debugging logs
#
# netwrite sends the message to the specified directory
#  and filename, without further manipulation
#  the directory must include a trailing slash
#  This is typically used to transfer logs between apps
##############################################################

import os
import glob
import time
import datetime
import sys
import re

def logWrite(progName, mymsg):
	logtime = datetime.datetime.utcnow()
	logfilename = "%s-%02u%02u%02u.log" % (progName, logtime.year % 100, logtime.month, logtime.day)
	localMsg = mymsg + "\n"
	try:
		f1 = open(logfilename, "a")
	except IOError as e:
		print ("Could not open log file: ", logfilename)
		print (" I/O error({0}): {1}".format(e.errno, e.strerror))
	else:
		f1.write(localMsg)
		f1.close()

# incorporate netWrite, only difference is dir path to network
def netWrite(curpath, curfn, msg):
	if os.path.isdir(curpath):
		pathAndFilename = curpath + curfn
		try:
			f2 = open(pathAndFilename, "w")
		except IOError:
			msg = "Could not open net file: " + pathAndFilename
			print (msg)
			logWrite(msg)
		else:
			msg = msg + "\n"
			try:
				f2.write(msg)
				f2.close()
			except IOError as e:
				print ("Error writing to net file: I/O error({0}): {1}".format(e.errno, e.strerror))
				logWrite("Error writing to net file: I/O error({0}): {1}".format(e.errno, e.strerror))


	else:
		print ("Cannot write to net log, path", curpath, "not available.")
		logWrite("Cannot write to net log, path" + " not available.")

