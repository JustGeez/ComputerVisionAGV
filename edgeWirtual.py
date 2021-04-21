from SimpleCV import *
#import freenect

disp = Display()
js = JpegStreamer('0.0.0.0:8081')
kin = VirtualCamera("/media/user/LG External HDD/AGVTestFootage/Example6.mp4", "video")

def program():
#input = raw_input("Which example would you like to run? ")
  direction = "left"#raw_input("Which fork direction should the AGV prefer? ")
  print direction + " edge preferred"
#kin = Kinect()

  while disp.isNotDone():
	img1 = kin.getImage().scale(0.5)
	img2 = img1.crop(50,190,220,10).toHSV().binarize().erode().dilate(iterations=2)
	
	blobs2 = img2.findBlobs().sortX()
	
	draw1 = img1.dl()
	draw1.rectangle((50,190), (220,10), Color.GREEN, width=2)
#	draw2 = img2.dl()
	leftL = blobs2[0]

	if (blobs2.count() == 2 ):
		rightL = blobs2[1]
		xR = blobs2[1].x
		yR = blobs2[1].y
		draw1.circle((rightL.x+50, rightL.y+190), 5, Color.HOTPINK, 2, filled=True)
		draw1.rectangle((rightL.x+50-(rightL.width()/2),190), (rightL.width(), 10), Color.YELLOW, width=2)
		draw1.text("Right edge identified", (rightL.x+50, rightL.y+142.5), Color.HOTPINK)
#		draw2.circle((rightL.x + (rightL.width()/2), rightL.y), 5, Color.HOTPINK, 2, filled=True)
#		draw2.rectangle((rightL.x - (rightL.width()/2),0), (rightL.width(), 20), Color.YELLOW, width=2)

	xL = blobs2[0].x
	yL = blobs2[0].y
#	draw2.circle((leftL.x - (leftL.width()/2), leftL.y), 5, Color.RED, 2, filled=True)
#	draw2.rectangle((leftL.x - (leftL.width()/2),0), (leftL.width(), 20), Color.YELLOW, width=2)
	draw1.circle((leftL.x+50, leftL.y+190), 5, Color.RED, 2, filled=True)
	draw1.rectangle((leftL.x+50-(leftL.width()/2),190), (leftL.width(), 10), Color.YELLOW, width=2)
	draw1.text("Left edge identified", (leftL.x-50, leftL.y+142.5), Color.RED)

	centre = (img2.width/2)

	if (blobs2.count() == 2 and direction == "right"):
		point = rightL.x
	else:
		point = leftL.x

	error = centre - point
			
	if (error < 10):
		print "Right"
	
	if (error > 10):
		print "Left"

	img1.save(js.framebuffer)
#	img1.save(disp)	
#	img2.save(disp);

if __name__ == '__main__':
  program()
	
