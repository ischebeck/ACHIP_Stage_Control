# -*- coding: utf-8 -*-
from time import sleep
import socket

class hexapod():
    '''A class for hexapod control with ASCII Commands'''
    def __init__(self, name):
        '''TODO: add limits for setting'''
        TCP_IP = '129.129.217.74'
        TCP_PORT = 2000
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((TCP_IP, TCP_PORT))
        self.mainName = name
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
    
    def send(self,command):
        
        self.soc.send(command)  
        data = self.soc.recv(4096).decode('UTF-8')
        print(data)
        
    def connect(self, axis):
        ###
        return True
    
    def disconnect(self, axis):
        ###
        self.soc.close()
        return True
    
    def getValue(self, axis):
        
        return 
    
    def setValue(self, axis, value):
        #self.pvList[axis][0].value = value
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