# -*- coding: utf-8 -*-
from time import sleep
import socket

class hexapod(multiplePV):
    '''A class for hexapod control with ASCII Commands'''
    def __init__(self, name):
        '''TODO: add limits for setting'''
        TCP_IP = '192.168.2.115'
        TCP_PORT = 17494
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((TCP_IP, TCP_PORT))
        self.mainName = name
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
    
    def send(self,command):
        self.soc.send(':'+command+'\n')           
    
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