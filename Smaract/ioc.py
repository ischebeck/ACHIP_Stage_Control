# -*- coding: utf-8 -*-
import time
from pcaspy import Driver, SimpleServer

prefix = 'SATSY01-DLAC080-DHXP:' #define PV’s for reading and setting the speed

pvdb = {
        'SMS': {'TYPE': str},
        'RMS': {'TYPE': str},
        }

class myDriver(Driver):

    def __init__(self):
        super(myDriver, self).__init__()

    def write(self, reason, msg):
        if reason == 'SMS': #if EPICS input SMS
            print('send command ', msg)     
            self.setParam(reason, msg)
            #send to hexapod
        return True

    def read(self, reason):
        if reason == 'RMS': #if EPICS input RBV (in progress)
            time.sleep(0.01)
            # reat return message
            value = 'RMS' + str(time.time())
            
            print ('rms ', value)
            return value

if __name__ == '__main__': #create PVs based on prefix and pvdb definition
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()
    while True:
        server.process(0.1) # process CA transactions