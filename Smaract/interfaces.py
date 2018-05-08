# -*- coding: utf-8 -*-
from time import sleep
import socket

class ECM():
    def __init__(self):
        #self.TCP_IP = '129.129.217.74'
        self.TCP_IP = 'ECM-00000029.psi.ch' 
        self.TCP_PORT = 2000
        self.ret = '' # last return message
        self.isConnected = False
                        
    def connect(self):
        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect((self.TCP_IP, self.TCP_PORT))
            self.isConnected = True
            return True
        except:
            print('Check ECM connection.')
            self.isConnected = False
            return False

    def disconnect(self):
        self.soc.close()
        self.isConnected = False
        return True
        
    def sendRaw(self, cmd):
        if self.isConnected:
            try:
                self.soc.send(bytes((cmd+'\n').encode()))  
                self.ret = self.soc.recv(4096).decode('UTF-8')
            except:
                print('ECM Communication Error')
        else:
            print('Check ECM connection.')
            
        return self.ret

    def send(self, unit, cmd):
        self.setUnit(unit)
        if self.ret == '!0\r\n': 
            self.sendRaw(cmd)
            return True
        else:
            return False
        
    def setUnit(self, unit):
        cmd = '%unit '+str(unit)
        self.sendRaw(cmd)
        return self.ret
    

    
class hexapod():

    '''A class for hexapod control with ASCII Commands'''
    def __init__(self, name, ECM):
        self.mainName = name
        self.ECM = ECM
        self.unit = '1'
        self.stdFrq = 5000
        
    def connect(self):
        self.ECM.sendRaw('%unit-activated? '+self.unit)
        if self.ECM.ret == '0\r\n':
            self.ECM.sendRaw('%activate-unit '+self.unit)    
            return self.ECM.ret
        return True
    
    def disconnect(self):
        self.ECM.sendRaw('%unit-activated? '+self.unit)
        if self.ECM.ret == '1\r\n':
            self.ECM.sendRaw('%deactivate-unit '+self.unit)    
            return self.ECM.ret
        return True

    def send(self, cmd):
        return self.ECM.send(self.unit, cmd)
        
    def get6d(self):
        cmd = 'pos?'
        self.send(cmd)
        pos = self.ECM.ret
        if pos[0]!='!':
            return pos.split(' ')[:6]
        else:
            return [None, None, None, None, None, None]
    
    def set6d(self, pos):
        # pos contains all 6 target coordinates (list or array)
        if self.isPosReachable(pos):
            cmd = 'mov '
            for c in pos:
                cmd += str(c)+' '
            return self.send(cmd)
        else:
            return False

    def getPivot(self):
        # piv contains all 3 pivot coordinates
        cmd = 'piv?'
        self.send(cmd)        
        piv  = self.ECM.ret
        if piv[0]!='!':
            return piv.split(' ')[:3]
        else:
            return [None, None, None]
    
    def setPivot(self, piv):
        # piv contains all 3 pivot coordinates
        cmd = 'piv '
        for c in piv:
            cmd += str(c)+' '
        return self.send(cmd)        
    
    def setFrq(self, f):
        cmd = 'frq ' + str(f)
        return self.send(cmd)
        
    def isPosReachable(self, pos):
        # pos contains all 6 target coordinates (list)
        cmd = 'rea? '
        for c in pos:
            cmd+= str(c)+' '
        self.send(cmd)
        if self.ECM.ret == '1\r\n':
            return True
        else:
            print('Position not reachable. ', pos)
            return False
         
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
    
class smaractLinear():
    '''A class for Smaract linear control with ASCII Commands'''
    def __init__(self, name, ECM):
        self.mainName = name
        self.ECM = ECM
        self.unit = '0'
        self.stdFrq = 5000
        
    def connect(self):
        self.ECM.sendRaw('%unit-activated? '+self.unit)
        if self.ECM.ret == '0\r\n':
            self.ECM.sendRaw('%activate-unit '+self.unit)    
            return self.ECM.ret
        return True
    
    def disconnect(self):
        self.ECM.sendRaw('%unit-activated? '+self.unit)
        if self.ECM.ret == '1\r\n':
            self.ECM.sendRaw('%deactivate-unit '+self.unit)    
            return self.ECM.ret
        return True

    def send(self, cmd):
        return self.ECM.send(self.unit, cmd)
        
    def setFrq(self, ch, f):
        cmd = 'frq ' + str(ch) + ' ' + str(f)
        return self.send(cmd)
        
    def getPos(self, ch):
        cmd = 'pos? ' + str(ch)
        self.send(cmd)
        pos = self.ECM.ret
        if pos[0]!='!':
            return pos
        else:
            return None
        
    def setPos(self, ch, pos):
        cmd = 'mpa ' + str(ch) + ' ' + str(pos)
        return self.send(cmd)
        
    def movState(self, ch):
        cmd = 'sta? ' + str(ch)
        self.send(cmd)
        return self.ECM.ret[0]
    
    def isHome(self, ch):
        cmd = 'ref? ' + str(ch)
        self.send(cmd)
        if self.ECM.ret == '1\r\n':
            return True
        return False

    def home(self, ch, autoZero = False):
        if not autoZero:
            cmd = 'ref ' + str(ch) + ' b ' + '0' 
        if autoZero:
            cmd = 'ref ' + str(ch) + ' b ' + '1'
        return self.send(cmd)

    def stop(self, ch):
        cmd = 'stop ' + str(ch)
        return self.send(cmd)
         