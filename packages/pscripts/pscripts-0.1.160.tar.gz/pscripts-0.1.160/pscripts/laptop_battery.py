#!/usr/bin/env python
import datetime, math
import logging as log
root_logger = log.getLogger()
log.basicConfig(format='%(message)s', level=log.DEBUG)

def getIntFromFile(filename):
    return int(open(filename).read())

charge_dir = "/sys/class/power_supply/sbs-4-000b/"
cur_charge_filename = charge_dir + "charge_now"
max_charge_filename = charge_dir + "charge_full"
empty_time_filename = charge_dir + "time_to_empty_avg"

def getTimeStringToEmpty():    
    time_to_empty = getIntFromFile(empty_time_filename)
    return str(datetime.timedelta(seconds=time_to_empty))

def getPercentLeft():
    cur_charge = getIntFromFile(cur_charge_filename)
    max_charge = getIntFromFile(max_charge_filename)
    perc_discharge = cur_charge / max_charge
    return math.ceil(perc_discharge * 100)

def _test():
    log.debug("Current charge of battery filename: " + cur_charge_filename)
    cur_charge = getIntFromFile(cur_charge_filename)
    log.debug("Current charge value: " + str(cur_charge))

    perc_discharge = getPercentLeft()
    log.debug("Percent discharge: " + str(perc_discharge) + "%")

    timeToEmpty = getTimeStringToEmpty()
    log.debug("Time to discharge: " + timeToEmpty)

if __name__ == '__main__':
    _test()
    
