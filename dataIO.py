'''
Loads and Saves Data
'''

import numpy as np

def load_data(filename):
    data = np.loadtxt(filename,delimiter=',')
    return data

def save_data (fileName, data):
    np.savetxt(fileName, data, fmt="%f", delimiter=',', newline="\n")
    return 0

def print_report(  position_low, position_high, scan_velocity, Nsamples, scan_frequency, time_of_scan, scan_filename):
    print('\n\n||----------------------  SCAN REPORT  ----------------------------||\n')
    print('Start Position:         '+str(position_low)+' mm')
    print('Final Position;         '+str(position_high)+' mm')
    print('Scanner Velociety:      '+str(scan_velocity)+' mm/s, unless you changed something.\n')
    print('Number of Data:         '+str(Nsamples))
    print('Acquisition Frequency:  '+str(scan_frequency)+' Hz')
    print('Time of Scan:           '+str(time_of_scan)+' s\n')
    print('Filename:               '+str(scan_filename))
    print('\n||-----------------------------------------------------------------||\n\n')
    return None
