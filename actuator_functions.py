## Newport SMC100   Actuator functions
## Eric Peach
## EP 495 Design Project, 10 March 2015

# eric.peach@gmail.com

# To the software archaeologist, here's how this thing works. The reference manual found at

#      http://assets.newport.com/webDocuments-EN/images/SMC100CC_And_SMC100PP_User_Manual.pdf

# describes a variety of commands that we can use like OR, PW, PA that issue commands like "Execute homing",
# "Change Mode" or "Position Absolute".

# A Command, which looks like      1PW0{carriage return}{newline}     must get encoded to hex characters like
#                                       \x31\x50\x57\x30\x0d\x0a
# and then sent to device with    ser.write('\x31\x50\x57\x30\x0d\x0a')

# results from the device can be read with ser.readline()

# once you have that to work with, it's pretty intuitive. Just CTRL-F search for commands in the manual and
# figure out how to convert them to hex. My file 'serial_commands.py' has some functions that do this for you.

# Feel free to email me for the code if you can't find it.



import serial

class SerialInterface:
	def __init__ (self,serial_in):
		self.ser = serial_in
		return None

	def home(self):
		# Makes the device attempt homing.
		self.ser.write('\x31\x50\x57\x30\x0d\x0a')	# Ensure NOT REFERENCED STATE
		self.ser.write('\x31\x4f\x52\x0d\x0a')		# Execute HOMING
		return None

	def current_position (self):
		self.ser.write('\x31\x54\x50\x0d\x0a')
		pos = self.ser.readline()
		return float(pos[3:12])

	def position_absolute(self, destination):
		# Positions the actuator at absolute value specified by float destination (in mm)
		target = str(int(destination*1000.0)/1000.0)
		cmd = self._encode_command( self._string_to_hex( "1PA"+target ) )
		self.ser.write(cmd+"\x0d\x0a")
		return None

	def position_relative(self, amount):
		# Positions the actuator at relative value specified by float amount
		target = str(int(amount*1000.0)/1000.0)
		cmd = self._encode_command( self._string_to_hex( "1PR"+target ) )
		self.ser.write(cmd+"\x0d\x0a")
		return None

	def status(self):
		# Returns whether the device is ready or not.

			# Status code 0 means not referenced.
			# status code 1 means configuration
			# status code 2 means ready!!
			# anything else and there's a problem.

		self.ser.write('\x31\x54\x53\x0d\x0a')
		sc = self.ser.readline()
		code = sc[7:9]

		if code=="0A":   status_code = 1
		elif code=="0B": status_code = 1
		elif code=="0C": status_code = 1
		elif code=="0D": status_code = 1
		elif code=="0E": status_code = 1
		elif code=="0F": status_code = 1
		elif code=="10": status_code = 1
		elif code=="11": status_code = 1
		elif code=="14": status_code = 2
		elif code=="32": status_code = 0
		elif code=="33": status_code = 0
		elif code=="34": status_code = 0
		elif code=="35": status_code = 0
		else:		 status_code = -1

		return status_code

	def status_verbose (self):
		# Returns a string describing the device's state.
		self.ser.write('\x31\x54\x53\x0d\x0a')
		sc = self.ser.readline()
		code = sc[7:9]

		if code=="0A":   result = "NOT REFERENCED from RESET"
		elif code=="0B": result = "NOT REFERENCED from HOMING"
		elif code=="0C": result = "NOT REFERENCED from CONFIGURATION"
		elif code=="0D": result = "NOT REFERENCED from DISABLE"
		elif code=="0E": result = "NOT REFERENCED from READY"
		elif code=="0F": result = "NOT REFERENCED from MOVING"
		elif code=="10": result = "NOT REFERENCED ESP stage error"
		elif code=="11": result = "NOT REFERENCED from JOGGING"
		elif code=="14": result = "CONFIGURATION"
		elif code=="1E": result = "HOMING commanded from RS-232-C"
		elif code=="1F": result = "HOMING commanded by SMC-RC"
		elif code=="28": result = "MOVING"
		elif code=="32": result = "READY from HOMING"
		elif code=="33": result = "READY from MOVING"
		elif code=="34": result = "READY from DISABLE"
		elif code=="35": result = "READY from JOGGING"
		elif code=="3C": result = "DISABLE from READY"
		elif code=="3D": result = "DISABLE from MOVING"
		elif code=="3E": result = "DISABLE from JOGGING"
		elif code=="46": result = "JOGGING from READY"
		elif code=="47": result = "JOGGING from DISABLE"
		else:            result = "SOMETHING WEIRD MAAaannn! Check if the cable is connected."

		return result

	def _string_to_hex (self, str_in):
		# _string_to_hex takes a string of characters and outputs a string of
		# hex characters associated with the characters.

		# Eg. if you input
		#    >>> str_to_hex("abc123")
		#
		#	61 62 63 31 32 33

		string = str(str_in)
		result = ""
		for i in range(len(string)):
			hexChar = string[i].encode("hex")
			if i > 0:
				result = result + " "
			result = result + str(hexChar)
		return result

	def _encode_command (self, data):
		# _encode_command takes in a string of hex characters such as the ones
		# outputted by _string_to_hex and creates a weird hex string with
		# encased backslashes that can be written to serial.

		dataB = []
		data = data.split(' ')
		for i in range(len(data)):
			dataB.insert(i,int(data[i],16))
		x =  "".join(chr(i) for i in dataB)
		return x

