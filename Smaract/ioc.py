# -*- coding: utf-8 -*-
import time
from pcaspy import Driver, SimpleServer
from interfaces import ECM, hexapod, smaractLinear
import numpy as np

prefix = 'SATSY01-DLAC080-DHXP:' #PV prefix

pvdb = {
        'sendRaw': {'type': 'str',
                    'value': 'init'},
        'returnMsg': {'type': 'char',
                      'count': 100000},
        'connect': {'type': 'int',
                    'value': 0},
        'isConnected': {'type': 'int',
                        'value': 0},
        'hSet6d': {'type': 'float',
                   'count': 6,
                   'value': [0.,0.,0.,0.,0.,0.]},
        'hGet6d': {'type': 'float',
                   'count': 6,
                   'value': [0.,0.,0.,0.,0.,0.],
                   'scan': 0.1},
        }

class iocDriver(Driver):

    def __init__(self):
        super(iocDriver, self).__init__()
        self.ECM = ECM()
        self.hexpod = hexapod('hexapod', self.ECM)
        
    def write(self, reason, val):
        
        status = True
        
        if reason == 'sendRaw': #if EPICS input sendRaw
            msg = val
            print('send command ', msg)     
            self.setParam(reason, msg)
            #send and recieve from ECM
            returnMsg = self.ECM.sendRaw(msg)
            self.setParam('returnMsg', self.strToChr(returnMsg))
            
        if reason == 'connect':
            if val == True:
                self.ECM.connect()
                self.setParam('isConnected', 1)
            else: 
                self.ECM.disconnect()
                self.setParam('isConnected', 0)
            
        if reason == 'hSet6d':
            success = self.setParam(reason, val)
            if not success:
                status = False
        
        self.updatePVs()
        return status
        
    def read(self, reason):
        
        status = True
        
        if reason == 'hGet6d':
            #pos = self.hexpod.get6d()
            pos = self.getParam('hSet6d')
            if pos[0] != None:
                self.setParam(reason, pos)    
                
                return pos
            else: # reading errror
                status = False 
        
        self.updatePVs()
        return status
        
    def strToChr(self, msg): # convert string to character array
        return [ord(s) for s in msg]

    def chrToStr(self, msg): # convert character array to string
        return ''.join([chr(s) for s in msg])


if __name__ == '__main__': #create PVs based on prefix and pvdb definition
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = iocDriver()
    while True:
        server.process(0.1) # process CA transactions