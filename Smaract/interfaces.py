# -*- coding: utf-8 -*-
from time import sleep
import socket

class ECM():
    def __init__(self):
        '''TODO: add limits for setting'''
        self.TCP_IP = '129.129.217.74'
        self.TCP_PORT = 2000
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ret = '' # last return message
                        
    def connect(self):
        self.soc.connect((self.TCP_IP, self.TCP_PORT))
        return True

    def disconnect(self):
        self.soc.close()
        return True
        
    def sendRaw(self, cmd):
        self.soc.send(bytes((cmd+'\n').encode()))  
        self.ret = self.soc.recv(4096).decode('UTF-8')
        
        if self.ret == '!0': 
            return True
        else:
            return False

    def setUnit(self, unit):
        cmd = '%unit '+str(unit)
        ret = self.sendRaw(cmd)
        return ret
    
    def send(self, unit, cmd):
        ret = self.setUnit(unit)
        if ret:
            ret = self.sendRaw(cmd)
        return ret
    
class hexapod():

    '''A class for hexapod control with ASCII Commands'''
    def __init__(self, name, ECM):
        self.mainName = name
        self.ECM = ECM
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        self.unit = '1'
    
    def connect(self):
        ret = ECM.sendRaw('%activate-unit '+self.unit)    
        return ret
    
    def disconnect(self):
        ret = ECM.sendRaw('%deactivate-unit '+self.unit)    
        return ret

    def send(self, cmd):
        ECM.send(self.unit, cmd)
    
    def getValue(self, axis):
        
        return 

    def set6d(self, pos):
        # pos contains all 6 target coordinates ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        cmd = 'mov '
        for c in pos:
            cmd+= str(pos)+' '
        self.send(cmd)
        return 
        
    def isMoving(self, axis):
        ###
        return False
    
    def home(self, axis):
        ###
        return True
    
    def stopAll(self):
        ###
        return 