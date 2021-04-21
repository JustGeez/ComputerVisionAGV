#!/usr/bin/python
'''
Motion profile - manual:
This script forms an object to host the attributes of the manual control profile
'''

#motion control object for AGV - NB: dont forget to destruct
class motionProfile(object):
    # constructor
    def __init__(self, enabled, minSpeed, maxSpeed, curSpeed, direction, e_stop):
        self.enabled = enabled      # is this class active?
        self.minSpeed = minSpeed    # minimum speed for AGV
        self.curSpeed = curSpeed    # current AGV speed
        self.maxSpeed = maxSpeed    # maximum speed allowed for AGV command
        self.direction = direction  # current/last commanded direction
        self.e_stop = e_stop        # estop status
            
    # increases or decreases speed on command - UNUSED
    def speedOffset(self, velocity, halt=False):
        if (self.e_stop == True or self.enabled == False):
            return -1

        if (velocity == "speedDown" and halt==False):
            print "decrease speed"      #signal sender placeholder
            if (self.curSpeed > self.minSpeed):
                self.curSpeed -= 5;
            elif (velocity == "speedUp" and halt==False):
                print "increase speed"      #signal sender placeholder
                if (self.curSpeed < self.maxSpeed):
                    self.curSpeed += 5;
        else:
            if (halt == True):
                print "AGV stopped"
                self.curSpeed = 0
            print "no speed change"     #signal sender placeholder
        
        print self.curSpeed
    
    # sets steering direction on command
    def steering(self, port, direction, commander):
        if (self.e_stop == True or self.enabled == False):
            return

        if (direction == "left"):
            print "moving " + direction  #signal sender placeholder
            port.write("!G 01 -800\r")
            port.write("!G 02 -100\r")
        elif (direction == "right"):
            print "moving " + direction  #signal sender placeholder
            port.write("!G 02 800\r")
            port.write("!G 01 100\r")
        elif (direction == "forward"):
            print "moving " + direction   #signal sender placeholder
            port.write("!G 01 -800\r")
            port.write("!G 02 800\r")
        elif (direction == "backward"):
            print "moving " + direction
            port.write("!G 01 800\r")
            port.write("!G 02 -800\r")
	elif (direction == "pin_up"):
		com.pin_command("extend")
	elif (direction == "pin_down"):
		com.pin_command("retract")
	elif (direction == "led_on"):
		com.led_command("on")
	elif (direction == "led_off"):
		com.led_command("off")
	elif (direction == "kin_on"):
		com.kin_command("on")
	elif (direction == "kin_off"):
		com.kin_command("off")
        else:
            return

        self.direction == direction 
