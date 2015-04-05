# ep495-spectrometer
Control and Data Acquisition for EP 495 NIR Spectrometer.
Created by Eric Peach in March 2015.

## Motivation
The EP 495 NIR Spectrometer uses a Digilent Analog Discovery Module and a Newport SMC100 Linear Actuator to move a diffraction grating and gather data.
When this is manually done, there is a time delay between the execution of the move command and the beginning of data acquisition with the ADM.

A control software was developed to automate the scan, allowing multiple scans to be taken with no time delay. This allows for more accurate spectrosopic data.

If you have either
* A Digilent Analog Discovery Module or
* A Newport SMC100 Linear Actuator

This software may be of interest to you as it contains example code which can be adapted for other purposes with either piece of hardware.

## Dependencies
The software is written for a Linux platform with the Digilent Waveforms SDK (_http://digilentinc.com_) installed.

If the SDK is installed in Windows, the code can be adapted to work in Windows.

## Set Up
1. Download the files into a working directory.
2. Ensure that the ADM is connected via USB, and that the analog signal to the spectrometer photodiode detector is connected to the Orange analogue inputs.
3. Enusre that the Newport SMC100 Linear Actuator microcontroller is turned on and plugged into a serial port on the computer.
4. Determine the location of the SMC100 Linear Actuator by running '_ls /dev/_'. It should show up as 'ttyUSB0' or 'ttyS0' or something similar.
5. In _scanner.py_, modify Line 33 to reference the correct address to the serial port of the linear actuator.
6. If you are using Windows, modify Line 48 in _scanner.py_ to say 'dwf = cdll.dwf'.

## Execution
1. Configure *grain_scanner.py*. On Line 13 through 15, Set the grain name, scan date and trial number. I fyou wish to have multiple scans, set the number of scans in the parentheses on Line 30.
2. Execute the scan by typing
```
$ python ./grain_scanner.py
```
3. The scan results will be outputted into the same directory as CSV files, named according to the values set in Step 1.