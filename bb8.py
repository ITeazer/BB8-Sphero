from bluepy import btle

import time

class BB8(btle.DefaultDelegate):
	def __init__(self, deviceAddress):
		btle.DefaultDelegate.__init__(self)

		# Address type must be "random" or it won't connect.
		self.peripheral = btle.Peripheral(deviceAddress, btle.ADDR_TYPE_RANDOM)
		print 'connected successfully!'
		print 'initializing...'
		self.peripheral.setDelegate(self)
		
		self.seq = 0
		print 'init 1 done!'
		
		# Attribute UUIDs are identical to Ollie.
		self.antidos = self.getSpheroCharacteristic('2bbd')
		self.wakecpu = self.getSpheroCharacteristic('2bbf')
		self.txpower = self.getSpheroCharacteristic('2bb2')
		self.roll = self.getSpheroCharacteristic('2ba1')
		self.notify = self.getSpheroCharacteristic('2ba6')
		
		print 'init 2 done!'

		# This startup sequence is also identical to the one for Ollie.
		# It even uses the same unlock code.
		print 'Sending antidos'
		self.antidos.write('011i3', withResponse=True)
		print 'Sending txpower'
		self.txpower.write('\x0007', withResponse=True)
		print 'Sending wakecpu'
		self.wakecpu.write('\x01', withResponse=True)
		
		print 'init 3 done!'


	def getSpheroCharacteristic(self, fragment):
		return self.peripheral.getCharacteristics(uuid='22bb746f'+fragment+'75542d6f726568705327')[0]


	def dumpCharacteristics(self):
		for s in self.peripheral.getServices():
			print s
			for c in s.getCharacteristics():
				print c, hex(c.handle)


	def cmd(self, did, cid, data=[], answer=True, resetTimeout=True):
		# Commands are as specified in Sphero API 1.50 PDF.
		# https://github.com/orbotix/DeveloperResources/
		seq = (self.seq&255)
		#self.seq += 1
		sop2 = 0xfc
		sop2 |= 1 if answer else 0
		sop2 |= 2 if resetTimeout else 0
		dlen = len(data)+1
		chk = (sum(data)+did+cid+seq+dlen)&255
		chk ^= 255

		msg = [0xff, sop2, did, cid, seq, dlen] + data + [chk]
		#print 'cmd:', ' '.join([chr(c).encode('hex') for c in msg])
		# Note: withResponse is very important. Most commands won't work without it.
		self.roll.write(''.join([chr(c) for c in msg]), withResponse=True)


	def handleNotification(self, cHandle, data):
		#print 'Notification:', cHandle, data.encode('hex')
		pass

	def waitForNotifications(self, time):
		self.peripheral.waitForNotifications(time)


	def disconnect(self):
		self.peripheral.disconnect()


if __name__ == '__main__':

	# Connect by address. Use "sudo hcitool lescan" to find address.
	print 'start connecting'
	bb = BB8('F1:6F:DB:2B:3B:4F')

	# Dump all GATT stuff.
	#bb.dumpCharacteristics()

	# Request some sensor stream.
	bb.cmd(0x02, 0x11, [0, 80, 0, 1, 0x80, 0, 0, 0,   0])
	print 'connected successfully!'
	
	for i in range(26):
		# Set RGB LED colour.
		bb.cmd(0x02, 0x20, [254, i*10, 2, 0])
		# Wait for streamed data.
		bb.waitForNotifications(1.0)
	
	v = 100
	h = 0
	for j in range(100):
		print 'v: '+ repr(v)
		print 'h: '+ repr(h)
		bb.cmd(0x02, 0x30, [v, (h&0xff00)>>8, h&0xff, 1])
		bb.waitForNotifications(1000000.0)


	# Must manually disconnect or you won't be able to reconnect.
	bb.disconnect()
	print 'DISconnected successfully! 0'
	raw_input("Press Enter to continue 0...")

