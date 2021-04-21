#!/usr/bin/python
'''
The main script, this script houses the following:
- Flask server config - webhost
- Flask server methods
- Data capture methods
'''

from flask import Flask, render_template, request, json, jsonify
from SimpleCV import Kinect, JpegStreamer, VirtualCamera
from datetime import date as d
import manualControl as man
import autoControl as automatic
import nameChanger as nameChanger
import commander as com
import PIDcontroller as PID
import lineTracker as LT
import time as t
import sqlite3 as sql
import serial 
from random import sample, randrange

#>> Object definitions -----------------------------------------------------------------------------------------
class telemetry(object):
	def __init__(self, error_count):
		self.sys_active = False
		self.control_mode = "Auto"
		self.nav_mode = "Center"
		self.runtime = 0
		self.start_time = t.time()
		self.distance = -1
		self.mot_ampsA = -1
		self.mot_ampsB = -1
		self.bat_volt = -1
		self.error_count = error_count
		self.date = d.today()	#assumes system power cycles each day

	def postToDatabase(self, db_name):
		try:
			with sql.connect(db_name) as con:
				cur = con.cursor()
				cur.execute("INSERT INTO batVrun (BatteryVoltage, Runtime) VALUES (?,?)",(self.bat_volt, self.runtime))
				cur.execute("INSERT INTO mcurVrun (MotorCurrentA, MotorCurrentB, Runtime) VALUES (?,?,?)",(self.mot_ampsA, self.mot_ampsB, self.runtime))
				con.commit()
				msg = "Records successfully recorded"
		except:
			con.rollback()
			msg = "Data record failure!"
		finally:
			print msg
			con.close()

	
	def battQuery(self):
		#send query serial to motor controller at defined intervals, assigns data to class property
		#  bat_volt
		# also checks bat_volt not low (require calibration)
		port.write("?V\r")
		rcv = port.readline()

		count = 0
		string = ''
		for letter in rcv:
		        if letter == ":":
                		count += 1
		        if count == 2:
                		break
		        elif count == 1 and not(letter == ":"):
                		string += letter

		return str(float(string)/10)

	def curQuery(self):
		#send query serial to motor controller
		# mot_cur
		port.write("?BA\r")
		rcv = port.readline()

		count = 0
		string = ['0','0']
		curA = "0"
		curB = "0"

		for letter in rcv:
			if letter == "=" or letter == ":":
				count += 1
				continue
			if letter <> "" and count == 1:
				curA += letter
			elif letter <> "" and count == 2:
				curB += letter
		
		if len(string) >= 2:
			string[0] = str(float(curA)/10)
			string[1] = str(float(curB)/10)

		return string
		
class visionSensor(object):
	def __init__(self):
		self.point = [0,0]
		self.camera1 = Kinect()#VirtualCamera("/home/user/Desktop/AGVTestFootage/Example6.mp4","video")#Kinect()# auto video input
#		self.camera2 = Kinect()#VirtualCamera("/home/user/Desktop/AGVTestFootage/Example6.mp4","video")#Kinect()# auto video input
		self.stream1 = JpegStreamer("0.0.0.0:8081") # auto control stream
#		self.stream2 = JpegStreamer("0.0.0.0:8082") # manual control stream
# Object definitions end -------------------------------------------------------------------------------------

# Function definitions ---------------------------------------------------------------------------------------
def createNewDatabase():
	try:
		date = str(d.today())
		conn = sql.connect('dbs/database_'+date+'.db')
		print "Opened database successfully"
		conn.execute('CREATE TABLE batVrun (BatteryVoltage NUMBER, Runtime NUMBER)')
		print "Table1 created successfully"
		conn.execute('CREATE TABLE mcurVrun (MotorCurrentA NUMBER, MotorCurrentB NUMBER, Runtime NUMBER)')
		print "Table2 created successfully"
#		conn.execute('CREATE TABLE mcurVstage (MotorCurrentA NUMBER, MotorCurrentB NUMBER, Stage NUMBER)')
#		print "Table3 created successfully"
		conn.execute('CREATE TABLE errorVrun (Error NUMBER, Runtime NUMBER)')
		print "Table4 created successfully"
#		conn.execute('CREATE TABLE cycletimeVerror (CycleTime NUMBER, Runtime NUMBER)')
#		print "Table5 created successfully"
#		conn.execute('CREATE TABLE speedVrun (Speed NUMBER, Runtime NUMBER)')
#		print "Table6 created successfully"
#		conn.execute('CREATE TABLE speedVstage (Speed NUMBER, Stage NUMBER)')
#		print "Table7 created successfully"
		conn.close()
		msg = "New database created successfully"
	except:
		msg = "Database already exists!"
	finally:
		print msg

# Function defintions end ------------------------------------------

# Object instantiations:
app = Flask(__name__)
manu = man.motionProfile(False, 0, 30, 5, 'center', False)	#set max, min and starting speed //Possible acceleration change too
auto = automatic.motionSettings(False, 0,  0, False, 'left')	#set active status, navigation mode, estop and debug status
tel = telemetry(0)
vis = visionSensor()
pid = PID.PID(1, 0, 0, 160)

# General instantiations:
createNewDatabase()
com.activate_GPIO()
com.kin_command("on")

# Variables
port = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)

# The function to deliver the home/auto page
@app.route('/')
def main():
	batVolt = tel.battQuery()
	motCur = tel.curQuery()
	t.sleep(0.05)	
	tel.runtime = t.time() - tel.start_time # keeping runtime record
	tel.nav_mode = auto.nav_mode
	tel.bat_volt = batVolt
	tel.mot_ampsA = motCur[0]
	tel.mot_ampsB = motCur[1]
	print tel.bat_volt
	tel.postToDatabase("dbs/database_"+str(d.today())+".db")

    #Telemetry assigner
	sys_active = tel.sys_active
	control_mode = tel.control_mode
	nav_mode = tel.nav_mode
	runtime = tel.runtime
	distance = tel.distance
	mot_ampsA = tel.mot_ampsA
	mot_ampsB = tel.mot_ampsB
	bat_volt = tel.bat_volt
	error_count = tel.error_count
	e_stop = auto.e_stop

	auto.progressUpdate(False) #remove eventually, replace with linetracker trigger

	prog = auto.progress
	print prog
	
	#Passes Python variable values onto web front-end
	return render_template('index.html',prog=prog,sys_active=sys_active,control_mode=control_mode,nav_mode=nav_mode,runtime=runtime,distance=distance,mot_ampsA=mot_ampsA, mot_ampsB=mot_ampsB,bat_volt=bat_volt,error_count=error_count,e_stop=e_stop)

#The function to await commands pulsed by the home/auto page
@app.route('/<command>')
def setting(command=None):
	tel.nav_mode = auto.nav_mode
	print tel.sys_active	# optional
	if (command == "estop"):	# estop web button pushed
		manu.e_stop = True
		auto.e_stop = True
		manu.enabled = False
		auto.enabled = False
		print "Estop activated!"

	elif (command == "safe"):	# safe web button pushed
		manu.e_stop = False
		auto.e_stop = False
		tel.sys_active = True
		print tel.sys_active
		print "Estop deactivated :)"
		print "System now active"

	elif (command == "automatic" and auto.e_stop == False): # auto web button pushed, checks e_stop
		manu.enabled = False
		auto.enabled = True
		tel.control_mode = "Auto"

		print "Manual mode disabled"
		print "Automatic mode enabled"
		
		#Begins interruptable automatic operation mode
		while not(auto.e_stop):
			point = vis.point
			correction = pid.update(point[1])
			auto.positionTracker(vis.camera1)
			vis.point = LT.LineTracker(vis.point[1]+correction, vis.camera1, vis.stream1, auto.direction, port, com)
			#check line area
			if point[1] - point[0] > 0:
				port.write("!G 01 -" + str(200+abs(correction))+"\r\n")
				port.write("!G 02 0\r\n")
			elif point[1] - point[0] < 0:
				port.write("!G 02 " + str(200+abs(correction))+"\r\n")
				port.write("!G 01 0\r\n")
			auto.lineTrackingDebug(pid.getPoint(), vis.point[1], correction)

	elif (command == "manual" and manu.e_stop == False):	# manual web button pushed, checks e_stop
		auto.enabled = False
		manu.enabled = True
		tel.control_mode = "Manual"
		print "manual stream started"
		while not(manu.e_stop):
			LT.OpenLoop(vis.camera1,vis.stream2)
		print "Automatic mode disabled"
		print "Manual mode enabled"
	elif (auto.e_stop == True or manu.e_stop == True):
		print("Estop still active!")	#Placeholder
		
	elif (auto.e_stop == False and manu.e_stop == False):	# checks e_Stop
		if (command == "center"):
			auto.nav_mode = "center"
			print "Navigation mode: Center"
		elif (command == "outer"):
			auto.nav_mode = "outer"
			print "Navigation mode: Outer"

	return render_template('index.html',sys_active=tel.sys_active,control_mode=tel.control_mode,nav_mode=tel.nav_mode,runtime=tel.runtime,distance=tel.distance,mot_ampsA=tel.mot_ampsA,mot_ampsB=tel.mot_ampsB,bat_volt=tel.bat_volt,error_count=tel.error_count,e_stop=auto.e_stop)

#Function to render and return the manual control page
@app.route("/remote_control/")
def remote_control():
    # keeping runtime record
	tel.runtime = t.time() - tel.start_time

	auto.enabled == False
	manu.enabled == True

	return render_template('control.html', runtime=tel.runtime)

#Function to wait for command pulse from manual web page and issue python script
@app.route("/remote_control/<movChange>")
def move(movChange=None):
	halt = False

	manu.steering(port, movChange, com)

	#manu.speedOffset(movChange, halt)

	return render_template('control.html')

#Function to render data capture page
@app.route("/data_capture/")
def data_capture():
	return render_template('data.html')

#From this point on, functions to display various data graphed

@app.route("/data_capture/batVrun")
def data_batVrun():
	return render_template('batVrun.html')

@app.route("/data_capture/mcurVrun")
def data_mcurVrun():
	return render_template('mcurVrun.html')

@app.route("/data_capture/errorVrun")
def data_errorVrun():
	return render_template('errorVrun.html')

@app.route("/data_capture/data_batVrun")
def fetch_batVrun():
	try:
		con = sql.connect("dbs/database_"+str(d.today())+".db")
		con.row_factory = sql.Row

		cur = con.cursor()
		cur.execute("SELECT * FROM batVrun")
		rows = cur.fetchall()
		msg = "Data retrieve success"
	except:
		msg = "Data retrieve error!"
	finally:
		print msg
		con.close()
	
	runtime = []
	battery = []

	for row in rows:
		runtime.append(str(int(row[1])))
		battery.append(int(row[0]))
	print battery

	return jsonify({'xvar' : runtime, 'yvar': battery})

@app.route("/data_capture/data_mcurVrun")
def fetch_mcurVrun():
	try:
		con = sql.connect("dbs/database_"+str(d.today())+".db")
		con.row_factory = sql.Row

		cur = con.cursor()
		cur.execute("SELECT * FROM mcurVrun")
		rows = cur.fetchall()
		msg = "Data retrieve success"
	except:
		msg = "Data retrieve error!"
	finally:
		print msg
		con.close()
	
	runtime = []
	mcur1 = []
	mcur2 = []

	for row in rows:
		runtime.append(str(int(row[2])))
		mcur1.append(int(row[0]))
		mcur2.append(int(row[1]))

	print runtime

	# presents two sequences in format [xvar: [g,h,i], yvar: [x,y,z],[a,b,c]]
	return jsonify({'xvar' : runtime, 'yvar1': mcur1, 'yvar2': mcur2})

@app.route("/data_capture/data_errorVrun")
def fetch_errorVrun():
	try:
		con = sql.connect("dbs/database_"+str(d.today())+".db")
		con.row_factory = sql.Row

		cur = con.cursor()
		cur.execute("SELECT * FROM errorVrun")
		rows = cur.fetchall()
		msg = "Data retrieve success"
	except:
		msg = "Data retrieve error!"
	finally:
		print msg
		con.close()
	
	runtime = []
	error = []

	for row in rows:
		runtime.append(str(int(row[1])))
		error.append(int(row[0]))
	print runtime

	return jsonify({'xvar' : runtime, 'yvar': error})

# admin-only tool, database checker
@app.route('/list')
def list():
	date = str(d.today())
	try:
		con = sql.connect('dbs/database_'+date+'.db')
		con.row_factory = sql.Row

		cur = con.cursor()
		cur.execute('SELECT * FROM batVrun')

		rows = cur.fetchall()
		msg = "'database_"+date+".db' located successfully :)"
	except:
		msg = "Cannot locate 'database_"+date+".db'!"
		rows = None
	finally:
		print msg

	return render_template('list.html', rows=rows)

# initiates the Flask web hosting framework when the script is run
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, threaded=True)
