import RPi.GPIO as GPIO
import os
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)

public_ips = ['8.8.8.8', '8.8.4.4', '208.67.222.222', '4.2.2.2', '1.1.1.1']

GATEWAY = '10.0.10.1'

def logSuccess(message):
	print("SUCCESS: " + message)

def logFailed(message):
	print("FAILED:" + message)

def turnOnPower():
	GPIO.output(11,GPIO.HIGH)

def turnOffPower():
	GPIO.output(11,GPIO.LOW)

def pingGateway():
	return os.system("ping -c 1 " + GATEWAY)

def validGatewayResponse():
	return pingGateway() == 0

def pingPublicIPs():
	responses = []
	for ip in public_ips:
		response = os.system("ping -c 1 " + ip)
		time.sleep(1)
		responses.append(response)
	return responses

def validPublicIPResponses(responses):
	return 0 in pingPublicIPs()

def wait(waitTime):
	print("Waiting" + str(waitTime) + " seconds")
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
	while True:
		longReboot()
		if validPublicIPResponses():
			logSuccess("Reaching Public IP")
			break
		else:
			logFailed("Reaching Public IP")
			wait(15)


def initialize():
	print("Initializing")
	turnOnPower()
	wait(10)

def run():
	while True:
		print("Pinging Gateway")
		if validGatewayResponse():
			logSuccess("Reaching Gateway")
			print("Pinging Public IPs")
			if validPublicIPResponses():
				logSuccess("Reaching Public IP")
			else:
				logFailed("Reaching Public IP")
				wait(15)
				print("Pinging Public IPs")
				if validPublicIPResponses():
					logSuccess("Reaching Public IP")
				else:
					logFailed("Reaching Public IP")
					print("Rebooting...")
					shortReboot()
					print("Pinging Public IPs")
					if validPublicIPResponses():
						logSuccess("Reaching Public IP")
					else:
						logFailed("Reaching Public IP")
						print("Rebooting...")
						rebootAndTestLoop()
		else:
			logFailed("Reaching gateway")



initialize()
run()
