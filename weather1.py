#!/usr/bin/env python2

##############################################################
# Weather1.py
# Reads data from an Arduino attached to various sensors
#  Validates the data and rewrites in the form of a CSV log
#  Works on Windows and Pi/Linux
# Colin Shaper, all rights reserved, 2017-2018
# This script runs with Python2, parentheses would need to be
#  added to print commands to allow it to work on Python3
##############################################################

import platform
import serial
import time
import re

from datetime import datetime
from LogWrite import logWrite, netWrite

progName = "weather1"
progName2 = "weather1b"
progVer  = "0.31"
progDate = "2018-12-10"
debugLevel = 0

# set global variables to silly values
tsl2561Lux = -1
si1145IR = -2
si1145UV = -3
si1145Vis = -4
guvaUV = -5
vemlUva = -10
vemlUvb = -11
vemlUvi = -12
ds18b20Sensor = -55
rainSensor = -9

# times each sensor was last read (overkill?) - these are strings, not dates
tsl2561LuxTime = "hhmmss"
si1145IRTime = "hhmmss"
si1145UVTime = "hhmmss"
si1145VisTime = "hhmmss"
guvaUVTime =  "hhmmss"
vemlUvaTime = "hhmmss"
vemlUvbTime = "hhmmss"
vemlUviTime = "hhmmss"
ds18b20SensorTime = "hhmmss"
rainSensorTime = "hhmmss"

delayTime = 0.1	# delay time
readErrorCount = 0

def isfloat(value):
	#print value
	try:
		float(value)
		return True
	except ValueError:
		print "Invalid float"
		return False


utcDT = datetime.utcnow()

pinetPath = "/nas/pinet/data/"
if platform.system() != 'Linux':
	pinetPath = "t:/Pinet/data/"

pinetFilename = "w1.dat"

def netWritexx(curpath, curfn, msg):
	# just prings msg as is, no logtime added
	fullfn = curpath + curfn
	try:
		fp = open(fullfn, "w")
	except IOError:
		print "Cannot open net file: ", fullfn
		return

	fp.write(msg)
	fp.close()

ser = 0  # just make a global variable, then set it by OS
if platform.system() != 'Linux':
	ser = serial.Serial('COM7', 9600, timeout=0)
else:
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)

hourmin = "%02u%02u" % (utcDT.hour, utcDT.minute)
previousHourmin = "%02u%02u" % (utcDT.hour, utcDT.minute -1)
hour = "%02u" % (utcDT.hour)
previousHour = "%02d" % (utcDT.hour-1)

logstr = "S1,%04u-%02u-%02u %02u:%02u:%02uZ" % \
	(utcDT.year, utcDT.month, utcDT.day, utcDT.hour, utcDT.minute, utcDT.second)
logstr += "," + progVer
logstr += ",Starting program"
logWrite(progName, logstr)
print logstr
logstr = "S2,hh:mm:ss,Temp ,R,Lux ,Suv ,Svs,Sir ,Guva,VemlA ,VemlB ,VemlIdx"
logWrite(progName, logstr)
print logstr

logstr = "S3,hh:mm:ss,Temp ,R,Lux ,Suv ,Svs,Sir ,Guva,VemlA ,VemlB ,VemlIdx"
logWrite(progName2, logstr)

while 1:
	lineOK = 0
	try:
		rline = ser.readline()
		readErrorCount = 0
		rline = rline.replace('\r', '').replace('\n', '')
		lineOK = 1
	except:
		readErrorCount = readErrorCount + 1
		print('Data could not be read')
		logstr = "E1,%04u-%02u-%02u %02u:%02u:%02uZ" % \
			(utcDT.year, utcDT.month, utcDT.day, utcDT.hour, utcDT.minute, utcDT.second)
		logstr += ",Cannot read from serial port,%u" % readErrorCount
		logWrite(progName, logstr)
		logWrite(progName2, logstr)
		lineOK = 0 # no further processing

	if lineOK:
		searchObj = re.search('(.*?): (.*)', rline)
		if searchObj:
			if searchObj.group(1) == "SIvis":
				if searchObj.group(2).isdigit():
					#print "Found Vis match: ", searchObj.group(2)
					si1145Vis = searchObj.group(2)
					utcDT = datetime.utcnow()
					si1145VisTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "SIir":
				if searchObj.group(2).isdigit():
					#print "Found IR match: ", searchObj.group(2)
					si1145IR = searchObj.group(2)
					utcDT = datetime.utcnow()
					si1145IRTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "SIuv":
				#print "1Found UV match: ", searchObj.group(2)
				if isfloat(searchObj.group(2)):
					#print "2Found UV match: ", searchObj.group(2)
					si1145UV = searchObj.group(2)
					utcDT = datetime.utcnow()
					si1145UVTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "TSLlux":
				if searchObj.group(2).isdigit():
					#print "Found Lux match: ", searchObj.group(2)
					tsl2561Lux = searchObj.group(2)
					utcDT = datetime.utcnow()
					tsl2561LuxTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "UV2ADC":
				# this is the result of the ADC conversion
				if searchObj.group(2).isdigit():
					#print "Found Rain match: ", searchObj.group(2)
					uv2SensorADC = searchObj.group(2)
					utcDT = datetime.utcnow()
					uv2SensorTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "Guva":
				# this is the calculated UV index, from UV2V / 10
				if isfloat(searchObj.group(2)):
					#print "Found UV2A match: ", searchObj.group(2)
					guvaUV = searchObj.group(2)
					utcDT = datetime.utcnow()
					guvaUVTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)

			elif searchObj.group(1) == "VEMLuva":
				# this is the calculated UV index, from UV2V / 10
				if isfloat(searchObj.group(2)):
					#print "Found UV2A match: ", searchObj.group(2)
					vemlUva = searchObj.group(2)
					utcDT = datetime.utcnow()
					vemlUvaTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "VEMLuvb":
				# this is the calculated UV index, from UV2V / 10
				if isfloat(searchObj.group(2)):
					#print "Found UV2A match: ", searchObj.group(2)
					vemlUvb = searchObj.group(2)
					utcDT = datetime.utcnow()
					vemlUvbTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "VEMLuvi":
				# this is the calculated UV index, from UV2V / 10
				if isfloat(searchObj.group(2)):
					#print "Found UV2A match: ", searchObj.group(2)
					vemlUvi = searchObj.group(2)
					utcDT = datetime.utcnow()
					vemlUviTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)

			elif searchObj.group(1) == "Temp":
				if isfloat(searchObj.group(2)):
					#print "Found Temp match: ", searchObj.group(2)
					ds18b20Sensor = searchObj.group(2)
					utcDT = datetime.utcnow()
					ds18b20SensorTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			elif searchObj.group(1) == "Rain":
				if searchObj.group(2).isdigit():
					#print "Found Rain match: ", searchObj.group(2)
					temp = int(searchObj.group(2))
					rainSensor = 1023 - temp
					utcDT = datetime.utcnow()
					rainSensorTime = "%02u:%02u:%02u" % (utcDT.hour, utcDT.minute, utcDT.second)
			
	hourmin = "%02u%02u" % (utcDT.hour, utcDT.minute)
	hour = "%02u" % (utcDT.hour)
	if previousHour != hour: # rewrite the header for convenience
		logstr = "S3,hh:mm:ss,Temp ,R,Lux ,Suv ,Svs,Sir ,Guva,VemlA ,VemlB ,VemlIdx"
		logWrite(progName2, logstr)
		previousHour = hour

	if previousHourmin != hourmin: # only output to the log once a minute
		logstr = "L1,%02u:%02u:%02u,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % \
			(utcDT.hour, utcDT.minute, utcDT.second, \
			ds18b20Sensor, ds18b20SensorTime, \
			rainSensor, rainSensorTime, \
			tsl2561Lux, tsl2561LuxTime, \
			si1145UV, si1145UVTime, \
			si1145Vis, si1145VisTime, \
			si1145IR, si1145IRTime, \
			guvaUV, guvaUVTime, \
			vemlUva, vemlUvaTime, \
			vemlUvb, vemlUvbTime, \
			vemlUvi, vemlUviTime \
			)
			
	
		print logstr
		logWrite(progName, logstr)

		oldestDate = "24:00:00"
		if rainSensorTime < oldestDate:
			oldestDate = rainSensorTime
		if guvaUVTime < oldestDate:
			oldestDate = guvaUVTime
		if si1145VisTime < oldestDate:
			oldestDate = si1145VisTime
		if si1145IRTime < oldestDate:
			oldestDate = si1145IRTime
		if si1145UVTime < oldestDate:
			oldestDate = si1145UVTime
		if tsl2561LuxTime < oldestDate:
			oldestDate = tsl2561LuxTime
		
		logstr = "L2,%02u:%02u:%02u,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % \
			(utcDT.hour, utcDT.minute, utcDT.second, \
			ds18b20Sensor, \
			rainSensor, \
			tsl2561Lux, \
			si1145UV, \
			si1145Vis, \
			si1145IR, \
			guvaUV, \
			vemlUva, \
			vemlUvb, \
			vemlUvi			
			)
		print logstr
		logWrite(progName2, logstr)
		
		logstr = "W1,%s,T%s,R%s,L%s,Su%s,v%s,i%s,g%s,Va%s,b%s,i%s" % \
			(oldestDate, \
			ds18b20Sensor, \
			rainSensor, \
			tsl2561Lux, \
			si1145UV, \
			si1145Vis, \
			si1145IR, \
			guvaUV, \
			vemlUva, \
			vemlUvb, \
			vemlUvi)
		netWrite(pinetPath, pinetFilename, logstr)

		previousHourmin = hourmin

	time.sleep(delayTime)


