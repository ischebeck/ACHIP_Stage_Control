# -*- coding: utf-8 -*-
import time
from pcaspy import Driver, SimpleServer
from interfaces import ECM, hexapod, smaractLinear
import numpy as np

prefix = 'SATSY01-DLAC080-DHXP:' #define PV’s for reading and setting the speed

pvdb = {
        'sendRaw': {'type': 'str',
                    'value': 'init'},
        'returnMsg': {'type': 'char',
                      'count': 100000},
        'connect': {'type': 'int',
                    'value': 0},
        'isConnected': {'type': 'int',
                    'value': 0},
                        
        }

class iocDriver(Driver):

    def __init__(self):
        super(iocDriver, self).__init__()
        self.ECM = ECM()
        self.ECM.connect()

    def write(self, reason, val):

        if reason == 'sendRaw': #if EPICS input sendRaw
            msg = val
            print('send command ', msg)     
            self.setParam(reason, msg)
            #send and recieve from ECM
            returnMsg = self.ECM.sendRaw(msg)
            self.setParam('returnMsg', self.strToChr(returnMsg))
            self.updatePVs()
            
        if reason == 'connect':
            if val == 1:
                self.ECM.connect()
                self.setParam('isConnected', 1)
            else: 
                self.ECM.disconnect()
                self.setParam('isConnected', 0)
                
        return True
        
    def strToChr(self, msg):
        return [ord(s) for s in msg]

    def chrToStr(self, msg):
        return ''.join([chr(s) for s in msg])


if __name__ == '__main__': #create PVs based on prefix and pvdb definition
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = iocDriver()
    while True:
        server.process(0.1) # process CA transactions