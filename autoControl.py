#!/usr/bin/python
'''
Motion profile - automatic:
This script forms an object to host the attributes of the automatic motion profile
'''

from SimpleCV import Kinect, Display, DrawingLayer, Blob, Color, JpegStreamer, VirtualCamera
import freenect
import colorTrack as color
import lineTracker as LT

class motionSettings(object):
	#constructor					DONT FORGET TO DESTRUCT!!
	def __init__(self, enabled, progress, nav_mode, e_stop, direction):
		self.enabled = enabled
		self.progress = progress
		self.nav_mode = nav_mode
		self.e_stop = e_stop 
		self.direction = direction
	
	# Looks for colored cards along path and relays position accordingly
	def positionTracker(self, camera):
		card_color = color.main()

		if card_color:
			if card_color == "red":
    				return 0
				
				if (self.progress >= 100):
    					self.progress = 0
				else:
					self.progress = 25

    			elif card_color == "green":
				return 1
				self.progress = 50

			elif card_color == "blue":
				return 2
				self.progress = 75

			elif card_color == "orange":
				return 3
				self.progress = 100

	def lineTrackingDebug(self, set_point, actual_point, correction):
		LT.main(set_point, actual_point, correction)

		
