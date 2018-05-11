# -*- coding: utf-8 -*-
import time
from pcaspy import Driver, SimpleServer
from interfaces import ECM, hexapod, smaractLinear

prefix = 'SATSY01-DLAC080-DHXP:' #define PV’s for reading and setting the speed

pvdb = {
        'SMS': {'type': 'str',
                'value': 'init'},
        'RMS': {'type': 'char',
                'value': 'init'},
        }

class iocDriver(Driver):

    def __init__(self):
        super(iocDriver, self).__init__()
        self.ECM = ECM()
        self.ECM.connect()

    def write(self, reason, msg):
        if reason == 'SMS': #if EPICS input SMS
            print('send command ', msg)     
            self.setParam(reason, msg)
            #send to ECM
            self.ECM.sendRaw(msg)
            
            #read-back from hexapod
            msg = self.ECM.ret
            print(msg)
            self.setParam('RMS', [ord[s] for s in msg])
            self.updatePVs()
        return True



if __name__ == '__main__': #create PVs based on prefix and pvdb definition
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = iocDriver()
    while True:
        server.process(0.1) # process CA transactions