# -*- coding: utf-8 -*-
from time import sleep
import socket

class ECM():
    def __init__(self):
        '''TODO: add limits for setting'''
        self.TCP_IP = '129.129.217.74'
        self.TCP_PORT = 2000
        self.ret = '' # last return message
        self.isConnected = False
                        
    def connect(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((self.TCP_IP, self.TCP_PORT))
        self.isConnected = True
        return True

    def disconnect(self):
        self.soc.close()
        self.isConnected = True
        return True
        
    def sendRaw(self, cmd):
        self.soc.send(bytes((cmd+'\n').encode()))  
        self.ret = self.soc.recv(4096).decode('UTF-8')
        return self.ret
        
    def setUnit(self, unit):
        cmd = '%unit '+str(unit)
        self.sendRaw(cmd)
        return self.ret
    
    def send(self, unit, cmd):
        self.setUnit(unit)
        if self.ret == '!0\r\n': 
            self.sendRaw(cmd)
            return True
        else:
            return False
    
class hexapod():

    '''A class for hexapod control with ASCII Commands'''
    def __init__(self, name, ECM):
        self.mainName = name
        self.ECM = ECM
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        self.unit = '1'
    
    def connect(self):
        self.ECM.sendRaw('%unit-activated? '+self.unit)
        if self.ECM.ret == '0\r\n':
            self.ECM.sendRaw('%activate-unit '+self.unit)    
            return self.ret
        return True
    
    def disconnect(self):
        self.ECM.sendRaw('%unit-activated? '+self.unit)
        if self.ECM.ret == '1\r\n':
            self.ECM.sendRaw('%deactivate-unit '+self.unit)    
            return self.ret
        return True

    def send(self, cmd):
        return self.ECM.send(self.unit, cmd)
    
    def get6d(self, axis):
        cmd = 'pos?'
        self.send(cmd)
        pos = self.ret
        print(pos)
        
    def set6d(self, pos):
        # pos contains all 6 target coordinates ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        cmd = 'mov '
        for c in pos:
            cmd+= str(c)+' '
        return self.send(cmd)
         
    def isMoving(self):
        cmd = 'mst?'
        self.send(cmd)
        if self.ECM.ret == '2\r\n':
            return True
        return False
    
    def isHome(self):
        cmd = 'ref?'
        self.send(cmd)
        if self.ECM.ret == '1\r\n':
            return True
        return False

    def home(self):
        cmd = 'ref'
        return self.send(cmd)

    def stopAll(self):
        cmd = 'stop'
        return self.send(cmd)
         