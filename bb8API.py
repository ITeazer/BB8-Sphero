#!/usr/bin/env python

import pygame

from bb8 import BB8
from time import sleep

class BB8API:
	
	DEFAULT_SPEED = 150
	DEFAULT_DIRECTION = 0
	
	
	def __init__(self, deviceAddress):	
		print 'Start connecting...'
		self.bb = BB8(deviceAddress)

		# Request some sensor stream.
		self.bb.cmd(0x02, 0x11, [0, 80, 0, 1, 0x80, 0, 0, 0,   0])
		print 'initialized successfully!'


	def move(self, speed, direction):
		''' speed - integer in range [0 .. 255]
			direction - integer in range [0 .. 359]'''
		v = speed
		h = direction
		print 'moving!   v: ' + repr(v) + '		h: ' + repr(h)
		self.bb.cmd(0x02, 0x30, [v, (h&0xff00)>>8, h&0xff, 1])
		#self.bb.waitForNotifications(1.0)


	def moveUp(self, time, speed = DEFAULT_SPEED):
		self.move(speed, 0)
		self.bb.waitForNotifications(100.0)
		sleep(time)
		#self.move(0,180)
		#sleep(0.75)


	def moveDown(self, time, speed = DEFAULT_SPEED):
		self.move(speed, 180)
		self.bb.waitForNotifications(1.0)
		sleep(time)
		#self.move(0,0)
		#sleep(0.75)


	def moveRight(self, time, speed = DEFAULT_SPEED):
		self.move(speed, 90)
		self.bb.waitForNotifications(1.0)
		sleep(time)
		#self.move(0,270)
		#sleep(0.75)


	def moveLeft(self, time, speed = DEFAULT_SPEED):
		self.move(speed, 270)
		self.bb.waitForNotifications(1.0)
		sleep(time)
		#self.move(0,90)
		#sleep(0.75)

		
	def moveStop(self):
		self.setColor(1,1)
		self.move(0,0)
		sleep(0.05)
		self.move(90,0)
		sleep(0.05)
		self.move(180,0)
		sleep(0.05)
		self.move(270,0)
		sleep(0.05)
		self.move(0,0)
		sleep(0.05)


	def setColor(self, r, g, b):
		self.bb.cmd(0x02, 0x20, [r, g, b, 0])


	def doCommand(self, command):
		directionText = command[0]
		direction = -1
		if directionText == 'U' or directionText == 'N':
			direction = 0
		elif directionText == 'R' or directionText == 'E':
			direction = 90
		elif directionText == 'D' or directionText == 'S':
			direction = 180
		elif directionText == 'L' or directionText == 'W':
			direction = 270
		else:
			return "wrong direction!"
		
		#print repr(command)
		
		time = float(int(command[2:6])) / 1000
		speed = int(command[7:-1])
		print repr(command) + ':				 direction: ' + repr(direction) + '	time: ' + repr(time) + '	speed: ' + repr(speed) 
		
		if directionText == 'U' or directionText == 'N':
			self.moveUp(time, speed)
		elif directionText == 'R' or directionText == 'E':
			self.moveRight(time, speed)
		elif directionText == 'D' or directionText == 'S':
			self.moveDown(time, speed)
		elif directionText == 'L' or directionText == 'W':
			self.moveLeft(time, speed)
		
		return "good!"
					
		

	def disconnect(self):
		# Must manually disconnect or you won't be able to reconnect.
		self.bb.disconnect()
		print 'DISconnected successfully!'
		raw_input("Press Enter to exit...")


		
	
if __name__ == '__main__':
	
	bb8 = BB8API('F1:6F:DB:2B:3B:4F')

	bb8.setColor(0,250,0)

	f = open("input.txt")
	commands = f.readlines()
	
	r = 250
	g = 0
	b = 0
	for command in commands:
		r ^= 250
		b ^= 250
		bb8.setColor(r,g,b)
		res = bb8.doCommand(command)
		print repr(res)
	
	bb8.disconnect()
