#!/usr/bin/env

## The Python Scanner

#%%-------------------------------------------
#          Import Files
#---------------------------------------------
import numpy as np
import serial
import time
from ctypes import *
from dwfconstants import *
from actuator_functions import SerialInterface
from dataIO import save_data, print_report



#%%##########################################################
#                                                           #
#                                                           #
#                Define Scan Function                       #
#                                                           #
#                                                           #
#############################################################

def execute_scan(position_low,position_high,scan_filename):

    #%%-------------------------------------------
    #          Define Constants
    #---------------------------------------------

    # Paths
    actuator_addr =  "/dev/ttyUSB0"

    # Scan Velocity and Frequency
    scan_velocity = 0.08		# mm/s
    scan_frequency = 4000.0       # Hz

    # Figure out the scan details
    time_of_scan = np.abs(position_high - position_low) / scan_velocity
    N_samples = int(np.ceil(time_of_scan * scan_frequency - 0.5))
    N_buffer = int(8000)                                                    # Can't be higher than 8192 (2^13)


    #%%-------------------------------------------
    #          Ctype Variables for ADM API
    #---------------------------------------------
    dwf = cdll.LoadLibrary("libdwf.so")                                     # our API we need. Raises troubles on Windows.
    hdwf = c_int()                                                          # Interface Handle instantiated
    acquisition_progress = c_byte()                                         # Instantiate the status of the acquisition.
    data_available= c_int()                                                 # Keeps track of available data during recording
    data_lost = c_int()                                                     # keeps track of lost data
    data_bad = c_int()                                                      # keeps track of corrupted data
    data_basket = ( c_double * N_buffer )()                                 # Collects data from device and unloads into array.
    sts = c_int()                                                           # System status. handy.


    #%%-------------------------------------------
    #          Connect to ADM
    #---------------------------------------------
    version = create_string_buffer(16)                                      # Our version, apparently.
    dwf.FDwfGetVersion(version)
    print "DWF Version: "+version.value

    print("Connecting to ADM Device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
    if hdwf.value == hdwfNone.value:
        print "Failed to open Device. Exiting now."
        quit()


    #%%-------------------------------------------
    #          Connect to Linear Actuator
    #---------------------------------------------

    # Create serial Connection and assign it to actuator.
    print('Connecting to Actuator')
    ser = serial.Serial(actuator_addr, 57600, timeout=1)
    Actuator = SerialInterface(ser)


    #%%-------------------------------------------
    #          Set Up Linear ACtuator
    #---------------------------------------------

    # Ensure that the actuator is in READY state. I.E. state code 32,33,34 or 35
    print('Checking Actuator Status...')
    status = Actuator.status()

    #print('status is' + str(status))

    if status == 0:
    	# Device is Ready
    	print('Status is READY. Excellent.')
    if status == 1:
    	# Device is Not Referenced
    	response = raw_input('The Actuator is Not Referenced. Attempt homing? (y/N): ')
    	if response == 'y' or response == 'Y':
    		Actuator.home()
    		print('\nAttempting Homing. Start the program again when the actuator')
    		print('stops moving.\n\n')
    	else:
    		print('\nDevice is not ready. Exiting.')
    	ser.close()
    	quit()
    elif status == 2:
    	# Device in Configuration Mode
    	raw_input('The Actuator is in Configuration Mode. Attempt homing? (y/N): ')
    	if response == 'y' or response == 'Y':
    		Actuator.home()
    		print('\nAttempting Homing. Start the program again when the actuator')
    		print('stops moving.\n\n')
    	else:
    		print('\nDevice is not ready. Exiting.')
    	ser.close()
    	quit()
    elif status == -1:
    	# Something Else. Print the verbose status and exit.
    	print('Something is wrong. We cannot begin scan. The device said:\n')
    	print ('\n         '+Actuator.status_verbose())
    	print ('\n... Exiting now.\n\n')
    	ser.close()
    	quit()

    #%%-------------------------------------------
    #          Move Actuator to Starting Position
    #---------------------------------------------

    # Figure out how long movement should take
    current_position = Actuator.current_position()
    print('Actuator is Currently at position '+str(current_position)+' mm.')

    time_remaining = 1.0 * np.abs(position_low - current_position) / scan_velocity

    print('Moving to Starting Position '+str(position_low)+' mm. ETA '+str(time_remaining)+' seconds.')
    Actuator.position_absolute(position_low)

    # Wait for predicted time and inspect difference. This is how we know we got there.
    time.sleep(time_remaining+1)
    if np.abs(Actuator.current_position() - position_low) >= 0.01:
    	print("ERROR! The Actuator Didn't arrive at Starting Position")
    	raise

    current_position = Actuator.current_position()

    print('Established at Starting Position of '+str(position_low)+'mm.')

    #%%--------------------------------
    #       Prepare ADM for Scan.
    #----------------------------------

    time.sleep(0.25)

    print ("Preparing ADM for Scan.")
    dwf.FDwfAnalogInAcquisitionModeSet (hdwf, acqmodeRecord)                # Set the device to Record Mode
    dwf.FDwfAnalogInRecordLengthSet    (hdwf, c_double(time_of_scan))       # Tell it to record for time.
    dwf.FDwfAnalogInFrequencySet       (hdwf, c_double(scan_frequency))     # Sets the acquisition Frequency to 100hz
    dwf.FDwfAnalogInBufferSizeSet      (hdwf, c_int(N_buffer))              # Sets the Acquisiton Buffer to 500 samples.
    dwf.FDwfAnalogInChannelEnableSet   (hdwf, c_int(0), c_bool(True))       # Enable the channel (0 ==> A1)
    dwf.FDwfAnalogInChannelRangeSet    (hdwf, c_int(0), c_double(10))	    # Set channel 0 to have range of 10

    time.sleep(2)                                                           # Wait at for the offset to stabilize (~2s)

    #%%-------------------------------------------
    #          Execute Scan
    #---------------------------------------------
    time_start = time.time()                                                # for debugging

    data_collected = []                                                     # Create a list to hold the gathered data.

    print('\n     ------BEGINNING SCAN-----    \n\nMoving to Final Position '+str(position_high)+' mm. ETA '+str(time_of_scan)+' seconds.')

    Actuator.position_absolute(position_high)                               # Order Actuator to Move

    dwf.FDwfAnalogInConfigure(hdwf, c_bool(True), c_bool(True))             # Order ADM to begin Recording


    # ----------------  Data Collection Loop runs around until AnalogInStatus says we're done. ---------------------

    while True:

        dwf.FDwfAnalogInStatusRecord( hdwf,byref(data_available),           # Record how many data are available in buffer
                                      byref(data_lost), byref(data_bad))

        dwf.FDwfAnalogInStatusData(hdwf, 0, data_basket, data_available)    # Download the available data into the basket.
        data_collected.append(data_basket[0:data_available.value])          # Empty the basket into data collected

        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(acquisition_progress))           # Tries to poll a status code from the device.
        if acquisition_progress.value == DwfStateDone.value :                         # If the status code == done, stop the loop.
            break
        time.sleep(0.5)                                                     # Should be << ( buffer size / scan rate )

    time_done = time.time()                                                 # for debugging

    # -----------------------  The Data Collection is done. Now harvest the remaining data ----------------------

    dwf.FDwfAnalogInStatusRecord( hdwf, byref(data_available),
                                  byref(data_lost),byref(data_bad))
    dwf.FDwfAnalogInStatusData(hdwf, 0, data_basket, data_available)
    data_collected.append(data_basket[0:data_available.value])

    time.sleep(1)

    # Make sure the Scanner actually got where it was supposed to.
    if np.abs(Actuator.current_position() - position_high) >= 0.01:
    	print("ERROR! The Actuator Didn't arrive at final position!")
    	raise

    print('\n     -----SCAN COMPLETE-----      \n\nEstablished at Final Position of '+str(position_high)+'mm.')


    #%%-------------------------------------------
    #          Close All Devices
    #---------------------------------------------
    dwf.FDwfDeviceCloseAll()

    Actuator.position_absolute(position_high)                               # Order Actuator to Return to Start Position

    ser.close()


    #%%-------------------------------------------
    #          Clean up the Data
    #---------------------------------------------
    print('scan time took ' + str(time_done-time_start))                    # For debugging

    scan_result = np.zeros(N_samples+2)                                     # Create the final numpy array by emptying collected
    cursor = 0                                                              # data into the array, watching indices carefully.
    for i in range(np.size(data_collected)):
        q = np.size(data_collected[i])
        if q > 0: scan_result[cursor:cursor+q] = np.array(data_collected[i])
        cursor += q

    scan_result = scan_result[2:]                                           # Zip off first two values.

    #%%-------------------------------------------
    #          Export the Data
    #---------------------------------------------

    xdata = np.linspace(position_low, position_high, N_samples)
    exportDataTable = np.vstack((xdata,scan_result)).T

    save_data(scan_filename, exportDataTable)
    print_report(  position_low,
                   position_high,
                   scan_velocity,
                   N_samples,
                   scan_frequency,
                   time_of_scan,
                   scan_filename)

#%%##########################################################
#                                                           #
#                                                           #
#                Define Main Function                       #
#                                                           #
#                                                           #
#############################################################
if __name__ == '__main__':

    # Paths
    scan_filename = "calibration_16March.dat"

    # Positions, in mm3.
    # 5.396

    execute_scan(11.9,3.6,scan_filename)






































