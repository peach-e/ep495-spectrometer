#!/usr/bin/env

import serial

#---------------------------------------------
#          Warning!!!!!
#---------------------------------------------

# There is a LOT of documentation I'm skipping over here. That's how it is though. Read the documentation at
# http://assets.newport.com/webDocuments-EN/images/SMC100CC_And_SMC100PP_User_Manual.pdf
# for more info on how this thing works.

#---------------------------------------------
#          String to Hex
#---------------------------------------------

def _string_to_hex (str_in):
	# _string_to_hex takes a string of characters and outputs a string of
	# hex characters associated with the characters.

	# Eg. if you input
	#    >>> str_to_hex("abc123")
	#
	#        61 62 63 31 32 33

	string = str(str_in)
	result = ""
	for i in range(len(string)):
		hexChar = string[i].encode("hex")
		if i > 0:
			result = result + " "
	        result = result + str(hexChar)
	return result


#---------------------------------------------
#          Encode_Command
#---------------------------------------------

def _encode_command (data):

	# _encode_command takes in a string of hex characters such as the ones
	# outputted by _string_to_hex and creates a weird hex string with
	# encased backslashes that can be written to serial.

	dataB = []
	data = data.split(' ')
	for i in range(len(data)):
		dataB.insert(i,int(data[i],16))
	x =  "".join(chr(i) for i in dataB)
	return x

#---------------------------------------------
#       Configuration_Mode (PW)
#---------------------------------------------

def Configuration_Mode (ser, param):
	# If param = 1, it Sets the device to CONFIGURATION MODE
	# If param = 0, it sets the device to NOT REFERENCED
	# if param is something else, it's assumed to be a query and
	# Returns the status of the controller.

	# Setting to NOT REFERENCED is required in order to start movement.

	if param == 1:
		ser.write('\x31\x50\x57\x31\x0d\x0a') # 1PW1
		sc = 1
	elif param == 0:
		ser.write('\x31\x50\x57\x30\x0d\x0a') # 1PW0
		sc = 0
	else:
		sc = ser.write('\x31\x50\x57\x3f\x0d\x0a') # 1PW?
	return sc

#---------------------------------------------
#       Execute Home Search (OR)
#---------------------------------------------

def Execute_Home_Search (ser):
	# Executes the home search.
	ser.write('\x31\x4f\x52\x0d\x0a')


#---------------------------------------------
#       Home Search Type (HT)
#---------------------------------------------

def Home_Search_Type (ser, home_type_value):
	# Describes how the home search should work.
	#	0 use MZ switch and encoder Index.
	#	1 use current position as HOME.
	#	2 use MZ switch only.
	#	3 use EoR- switch and encoder Index.
	#	4 use End of Run- switch only.
	#	? Tells you what it's currently set for

	cmd = _encode_command( _string_to_hex( home_type_value ) )
	sc = ser.write("\x31\x48\x54"+cmd+"\x0d\x0a")
	return sc

#---------------------------------------------
#          Position Absolute (PA)
#---------------------------------------------

def Position_Absolute (ser, target_value):
	# Positions the actuator at absolute value specified by
	target = str(int(target_value*1000.0)/1000.0)
	cmd = _encode_command( _string_to_hex( "1PA"+target ) )
	sc = ser.write(cmd+"\x0d\x0a")
	return sc

#---------------------------------------------
#          Position Relative (PR)
#---------------------------------------------

def Position_Relative (ser, target_value):
	# Positions the actuator at relative value specified by
	target = str(int(target_value*1000.0)/1000.0)
	cmd = _encode_command( _string_to_hex( "1PR"+target ) )
	sc = ser.write(cmd+"\x0d\x0a")
	return sc

#---------------------------------------------
#          Get System Status (Ts)
#---------------------------------------------

def Get_Status (ser):
	ser.write('\x31\x54\x53\x0d\x0a')
	sc = ser.readline()
	print("Position Error: "+sc[3:7])
	code = sc[7:9]

	if code=="0A":   print("NOT REFERENCED from reset")
	elif code=="0B": print("NOT REFERENCED from HOMING")
	elif code=="0C": print("NOT REFERENCED from CONFIGURATION")
	elif code=="0D": print("NOT REFERENCED from DISABLE")
	elif code=="0E": print("NOT REFERENCED from READY")
	elif code=="0F": print("NOT REFERENCED from MOVING")
	elif code=="10": print("NOT REFERENCED ESP stage error")
	elif code=="11": print("NOT REFERENCED from JOGGING")
	elif code=="14": print("CONFIGURATION")
	elif code=="1E": print("HOMING commanded from RS-232-C")
	elif code=="1F": print("HOMING commanded by SMC-RC")
	elif code=="28": print("MOVING")
	elif code=="32": print("READY from HOMING")
	elif code=="33": print("READY from MOVING")
	elif code=="34": print("READY from DISABLE")
	elif code=="35": print("READY from JOGGING")
	elif code=="3C": print("DISABLE from READY")
	elif code=="3D": print("DISABLE from MOVING")
	elif code=="3E": print("DISABLE from JOGGING")
	elif code=="46": print("JOGGING from READY")
	elif code=="47": print("JOGGING from DISABLE")

#---------------------------------------------
#          Get Current Position (TP)
#---------------------------------------------

def Get_Current_Position (ser):
	ser.write('\x31\x54\x50\x0d\x0a')
	pos = ser.readline()
	return pos[0:12]
#        ser.write('\x31\x54\x50\x0d\x0a')
#        sc = ser.readline()
#	print(sc)

#---------------------------------------------
#          Reset Controller (RS)
#---------------------------------------------

def Reset_Controller (ser):
        ser.write('\x31\x52\x53\x0d\x0a')
	print('Resetting Controller')


#---------------------------------------------
#          Open Serial
#---------------------------------------------
if __name__ == "__main__":
	ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)

	#x = _string_to_hex("1HT?")
	#cmd = _encode_command(x+" 0d 0a")
	#ser.write(cmd)
	#sc = ser.readline()
	#print(str(sc))

	Position_Absolute(ser,3.9)

	print(Get_Current_Position(ser))
	Get_Status(ser)
#	Reset_Controller(ser)
	ser.close()
