import RPi.GPIO as GPIO
import os
import time
from datetime import datetime
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)

public_ips = ['8.8.8.8', '8.8.4.4', '208.67.222.222', '4.2.2.2', '1.1.1.1']

GATEWAY = '192.168.1.1'

def LogEvent(message):
	date = datetime.now().strftime("%Y-%m-%d")
	time = datetime.now().strftime("%H:%M:%S")
	if os.path.exists("LOGS"):
		logfile = open("LOGS/{0}-LOG.txt".format(date), "a")
		logfile.write(time + " - " + message + "\n")
		logfile.close()
	else:
		os.mkdir("LOGS")
		logfile = open("LOGS/{0}-LOG.txt".format(date), "a")
		logfile.write(time + " - " + message + "\n")
		logfile.close()

def logSuccess(message):
	print("SUCCESS: " + message)
	
def logFailed(message):
	print("FAILED: " + message)
	LogEvent("FAILED: " + message)

def turnOnPower():
	GPIO.output(11,GPIO.HIGH)
	LogEvent("POWER RE-APPLIED")

def turnOffPower():
	GPIO.output(11,GPIO.LOW)
	LogEvent("POWER REMOVED")

def pingGateway():
	return os.system("ping -c 1 " + GATEWAY)

def validGatewayResponse():
	print("PINGING DEFAULT GATEWAY")
	return pingGateway() == 0

def pingPublicIPs():
	print("PINGING PUBLIC IPs")
	responses = []
	for ip in public_ips:
		response = os.system("ping -c 1 " + ip)
		time.sleep(1)
		responses.append(response)
	return responses

def validPublicIPResponses():
	return 0 in pingPublicIPs()

def wait(waitTime):
	print("Waiting " + str(waitTime) + " seconds")
	time.sleep(waitTime)

def shortReboot():
	turnOffPower()
	wait(150)
	turnOnPower()
	wait(300)

def longReboot():
	turnOffPower()
	wait(1800)
	turnOnPower()
	wait(300)

def rebootAndTestLoop():
	long_reboot_counter = 0
	while True:
		longReboot()
		long_reboot_counter += 1
		if validPublicIPResponses():
			logSuccess("Reaching Public IP")
			LogEvent("CONNECTIVITY RESTORED AFTER {0} REBOOT(S) - LEAVING POWER ON/RESTARTING LOOP".format(long_reboot_counter))
			break
		else:
			logFailed("REACHING PUBLIC IPs AFTER {0} ATTEMPTS".format(long_reboot_counter))
			wait(15)


def initialize():
	print("Initializing")
	turnOnPower()
	wait(10)

def run():
	while True:
		if validGatewayResponse():
			logSuccess("REACHING GATEWAY")
			if validPublicIPResponses():
				logSuccess("REACHING PUBLIC IPs")
			else:
				wait(30)
				if validPublicIPResponses():
					logSuccess("REACHING PUBLIC IPs")
				else:
					logFailed("REACHING PUBLIC IP - SECOND ATTEMPT")
					print("REBOOTING...")
					shortReboot()
					if validPublicIPResponses():
						logSuccess("REACHING PUBLIC IPs AFTER 1 REBOOT - RESTARTING LOOP")
						LogEvent("SUCCESS: REACHING PUBLIC IPs AFTER 1 REBOOT - RESTARTING LOOP") 
					else:
						logFailed("REACHING PUBLIC IPs AFTER 1 REBOOT - ENTERING LONG LOOP")
						print("REBOOTING...")
						rebootAndTestLoop()
		else:
			logFailed("REACHING DEFAULT GATEWAY" + " - " + GATEWAY)
			wait(10)
			

initialize()
run()
