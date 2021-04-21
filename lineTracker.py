#!/usr/bin/python
'''
Line tracking:
This scripts contains methods used for:
	- Identifying the AGV line path - navigation
	- Watching for area change in line path - event trigger
'''
from SimpleCV import Kinect, Display, DrawingLayer, Blob, Color, JpegStreamer, VirtualCamera, Camera
import freenect
import time

def LineTracker(target, kin, js, direction, port, com):   	
	img = kin.getImage().resize(320,240)

	xStartFocus = 0
	yStartFocus = 220
	xEndFocus = img.width - 2*xStartFocus 
	yEndFocus = 20

	track_top = img.crop(xStartFocus,yStartFocus,xEndFocus,yEndFocus).toHSV().binarize().erode(iterations=3).dilate()
	blobs_top = track_top.findBlobs()

	if blobs_top:
		# Line area checker, requires calibration
		blobs_top_area = blobs_top[-1].area()
		print blobs_top_area
		if blobs_top_area > 400 and blobs_top_area < 500:
			#stop
			port.write("!G 01 0\r\n")
			port.write("!G 02 0\r\n")
			#pin up
			com.pin_command("extend")

		elif blobs_top_area > 1000 and blobs_top_area < 1500:
			#stop
			port.write("!G 01 0\r\n")
			port.write("!G 02 0\r\n")
			#pin down
			com.pin_command("retract")

	# Illustration purposes
#	draw_layer = img.dl()
#	draw_layer.rectangle((xStartFocus,yStartFocus), (xEndFocus,yEndFocus), Color.GREEN, width=2)
	left_line = blobs_top[0]

	if (len(blobs_top) >= 2 ):
		right_line = blobs_top[1]
		x_right = blobs_top[1].x
		y_right = blobs_top[1].y
		# Illustration purposes
#		draw_layer.circle((right_line.x+xStartFocus, right_line.y+yStartFocus), 9, Color.HOTPINK, 2, filled=False)
#		draw_layer.rectangle((right_line.x+xStartFocus-(right_line.width()/2),yStartFocus), (right_line.width(), 2), Color.YELLOW, width=2)
#		draw_layer.text("Right edge identified", (right_line.x+100, right_line.y+285), Color.HOTPINK)

	x_left = blobs_top[-1].x
	y_left = blobs_top[-1].y

	# Illustration purposes
#	draw_layer.circle((left_line.x+xStartFocus, left_line.y+yStartFocus), 9, Color.RED, 2, filled=False)
#	draw_layer.rectangle((left_line.x+xStartFocus-(left_line.width()/2),yStartFocus), (left_line.width(), 2), Color.YELLOW, width=2)
#	draw_layer.text("Left edge identified", (left_line.x-100, left_line.y+285), Color.RED)

#	draw_layer.circle((int(target)+xStartFocus, left_line.y+yStartFocus), 7, Color.BLUE, 1, filled=True)
#	draw_layer.line((left_line.x+xStartFocus,left_line.y+yStartFocus),(int(target)+xStartFocus,left_line.y+yStartFocus), Color.BLUE, 1)
	centre = (track_top.width/2)

	point = [centre]

	# Sets focal point depending on operator decision, left or right line
	if (len(blobs_top) >= 2 and direction == "right"):
		point.append(right_line.x)
	else:
		point.append(left_line.x)
	
	track_top.save(js.framebuffer)
	
	# returns (x,y) coordinates of selected line centre
	return point

# Simply returns filtered image with centre-line for reference
def OpenLoop(kin, js):
	img = kin.getImage().resize(320,240).binarize().erode(iterations=7).dilate(iterations=3).crop(0,150,320,80)#.warp([(0,0),(160,0),(140,60),(20,60)])
	img = img.scale(2)
	draw = img.dl()
	draw.line((img.width/2,0),(img.width/2,img.height/2),Color.RED,width=4)
	img.save(js.framebuffer)


# Debugging purposes
def main(set_point, actual_point, correction):
	print "Setpoint: " + str(set_point) + "\n" + "Actual: " + str(actual_point) + "\r"
	print "Correction: " + str(correction) + "\n"
