#!/usr/bin/python
'''
Device commander:
The methods below are called to activate/deactivate the relay channels based on what 
device is required to be activated.
'''

import RPi.GPIO as gpio
import time

def activate_GPIO():
	gpio.setmode(gpio.BOARD) # Use board pin reference system

	gpio.setup(11, gpio.OUT) # pin down

	gpio.setup(13, gpio.OUT) # pin up

	gpio.setup(15, gpio.OUT) # led on/off

	gpio.setup(16, gpio.OUT) # kinect on/off
	

def pin_command(command):
    if command == "extend":
        # extend pin
	gpio.output(11, False)
	gpio.output(13, True)
	time.sleep(2.5)
	gpio.output(13, False)
    elif command == "retract":
        # retract pin
	gpio.output(13, False) 
	gpio.output(11, True)
	time.sleep(2.5)
	gpio.output(11, False)

def led_command(command):
    if command == "on":
        # led on 
	gpio.output(15, False)
    elif command == "off":
        # led off
	gpio.output(15, True)

def kin_command(command):
    if command == "on":
        # kinect on
	gpio.output(16, False)
    elif command == "off":
        # kinect off
	gpio.output(16, True)

def status_okay_command(command):
    if command == "on":
        # stat green on 
	gpio.output(18, False)
    elif command == "off":
        # stat green off 
	gpio.output(18, True)

def status_fault_command(command):
    if command == "on":
        # stat red on 
	gpio.output(22, False)
    elif command == "off":
        # stat red off
	gpio.output(22, True)
