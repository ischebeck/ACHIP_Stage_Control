# -*- coding: utf-8 -*-
import time
from pcaspy import Driver, SimpleServer

prefix = '' #define PV’s for reading and setting the speed

pvdb = {
        'VAL': {'TYPE': 'int'},
        'RBV': {'TYPE': 'float'},
        }

class myDriver(Driver):

    def __init__(self):
        super(myDriver, self).__init__()

    def write(self, reason, speedval):
        if reason == 'VAL': #if EPICS input VAL
            print('new speed is', speedval)     
            self.setParam(reason, speedval)
        return True

    def read(self, reason):
        if reason == 'RBV': #if EPICS input RBV (in progress)
            time.sleep(0.01)
            value = self.getParam(reason)
            print ('speed is '); print (value)
            return value

if __name__ == '__main__': #create PVs based on prefix and pvdb definition
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()
    while True:
        server.process(0.1) # process CA transactions