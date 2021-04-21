#!/usr/bin/python

import lineTracker as lt
from SimpleCV import *
import serial as s
import commander as com
import PIDcontroller as PID
import time as t
kin = Kinect()

port = s.Serial(port='/dev/ttyAMA0', baudrate=115200, parity=s.PARITY_NONE, stopbits=s.STOPBITS_ONE, bytesize=s.EIGHTBITS, timeout=0.01)
pid = PID.PID(0.09,0,0.08,160)

def main(js, com):
	point=lt.LineTracker(0, kin, js, "left", port, com)
	print point
	correction = pid.update(point[1])
	correction = (abs(correction)/100)*400
	if point[1] - point[0] > 0:
		port.write("!G 02 " + str(200+abs(correction)) + "\r\n")
		port.write("!G 01 10\r\n")
	elif point[1] - point[0] < 0:
		port.write("!G 01 -" + str(200+abs(correction)) + "\r\n")
		port.write("!G 02 -10\r\n")

if __name__ == '__main__':
	com.activate_GPIO()
	try:
		js = JpegStreamer("0.0.0.0:8081")
	except:
		print "Stream failed to start"
	finally:
		print "Stream started"
	while True:
		main(js, com)
