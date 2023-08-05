# -*- coding: utf-8 -*-
# Author: Stein-Otto Svorstol
# steinotto.svorstol@gmail.com // essoen.net
import requests, time, pynma
from sys import stdin

def main():
	#Times the call for checkCoffeeMaker
	print("AbakaffeNotifer is running.")
	now = time.time()
	lastCheck = now
	lastStart = checkCoffeemaker("")
	while True:
		now = time.time()
		if (now >= lastCheck + 60*3 ): # Check every three minutes
			lastCheck = now
			lastStart = checkCoffeemaker(lastStart)

def addAllKeys(nma): # Adds API-keys from file
	for linje in stdin:
		nma.addkey(linje)

def checkCoffeemaker(lastStart):
	data = getData()
	currentStatus = data["status"]
	newStart = data["last_start"]
	if (currentStatus and newStart != lastStart):
		print("The coffee maker is on. It was turned on " + newStart+ ".")
		lastStart = newStart
		notifyPhone(newStart)
		return lastStart 
	else:
		print("Coffee maker is not on. The last time was " + newStart + ".")
		return lastStart


def notifyPhone(time):
	# Sends POST to NotifyMyAndroid
	app = "CoffeeNotifier"
	event = "Coffee is ready!"
	descr = "Turned on: "  + time 
	p.push(app, event, descr)

def getData():
	r = requests .get("http://kaffe.abakus.no/api/status")
	return r.json()["coffee"]

p = pynma.PyNMA("")
addAllKeys(p)
main()