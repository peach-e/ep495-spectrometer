## Grain Scanner
from scanner import execute_scan
from os import system

######################################################################
#
#                     Scan Filename Format:
#
#            scan_filename = "GRAINNAME_SCANDATE_TRIALNO_SCANNO.dat"
#
######################################################################

grain_name = "Plot-241"
scan_date = "16Mar"
trial_number = 1


## Check to make sure you don't overwrite your data.
print('Grain Sample : ' + grain_name)
print('Scan Date    : ' + scan_date)
print('Trial Number : ' + str(trial_number))

response = raw_input('Confirm the settings?  ')
if not(response == 'y' or response == 'Y'):
    print('Aborting')
    quit()



for scan_number in range(5):
    # Switches the direction of scan depending on even or odd scan.
    if scan_number%2 == 0:
        position_low = 3.6
        position_high = 11.9
    else:
        position_low = 11.9
        position_high = 3.6

    # Prepare file name
    filename = grain_name + "_" + scan_date + "_trial-" + str(trial_number) + "_scan-" + str(scan_number) + ".dat"

    # Do Scam
    execute_scan(position_low,position_high,filename)


print('Batch Scan has finished')

























