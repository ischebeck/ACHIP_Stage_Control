# -*- coding: utf-8 -*-
from epics import PV
from time import sleep
class multiplePV(object):
    '''
    A class describing a collection of PVs.
    Implements the destructor to disconnect the PVs
    '''
    def __init__(self):
        self.pvList = {}

    def __del__(self):
        try:
            for pv in self.pvList:
                self.pvList[pv].disconnect()
        except Exception as e:
            print('Warning: destructor not working correctly')
            print(e)
        pass

class hexapod(multiplePV):
    '''A class for hexapod control with expics'''
    def __init__(self, name):
        '''TODO: add limits for setting'''
        self.mainName = name
        self.pv_X = PV(self.mainName + ':-SET')
        self.pv_Xrb = PV(self.mainName + ':-READ')
        self.pv_Y = PV(self.mainName + ':-SET')
        self.pv_Yrb = PV(self.mainName + ':-READ')
        self.pv_Z = PV(self.mainName + ':-SET')
        self.pv_Zrb = PV(self.mainName + ':-READ')
        self.pv_Alpha = PV(self.mainName + ':-SET')
        self.pv_Alpharb = PV(self.mainName + ':-READ')
        self.pv_Beta = PV(self.mainName + ':-SET')
        self.pv_Betarb = PV(self.mainName + ':-READ')
        self.pv_Gamma = PV(self.mainName + ':-SET')
        self.pv_Gammarb = PV(self.mainName + ':-READ')
        self.pvON = PV(self.mainName + ':')
        self.pvList = {'x': [self.pv_X, self.pv_Xrb], 'y': [self.pv_Y, self.pv_Yrb], 'z': [self.pv_Z, self.pv_Zrb], 
                       'alpha': [self.pv_Alpha, self.pv_Alpharb], 'beta': [self.pv_Beta, self.pv_Betarb], 'gamma': [self.pv_Gamma, self.pv_Gammarb]}
        
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
                    
    def connect(self, axis):
        ###
        return True
    
    def disconnect(self, axis):
        ###
        return True
    
    def getValue(self, axis):
        def function():
            return self.pvList[axis][1].value
        return function
    
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