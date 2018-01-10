# PyQt5 imports
# from PyQt5 import QtWidgets, Qt, uic
# from PyQt5.QtCore import pyqtSlot, QTimer, QSize
# PyQt4 imports
from PyQt5.QtCore import pyqtSlot, QTimer, QThread, QSize
from PyQt5 import uic, Qt
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QSizePolicy
#from axes_canvas import AxesCanvas
#from axes_limits import AxesLimits
from interfaces import hexapod
from time import time, sleep
import numpy as np

'''
NOTE:
    deviceControl : interaction with machine
    deviceWidget  : UI element with buttons, no interaction with machine

'''

def init_spinbox(guiElem, settings):
    guiElem.setDecimals(settings['ndec'])
    guiElem.setSingleStep(settings['step'])
    guiElem.setRange(min(settings['range']), max(settings['range']))
    guiElem.setSuffix(settings['suffix'])


# Controllers
class ControlWithRefresh(QtWidgets.QWidget):

    def __init__(self, refresh=1000, parent=None):
        super().__init__(parent=parent)
        self.timeout = refresh
        self.timer = QTimer()
        self.threadRefresh = Executor(self.refresh)
        self.timer.setInterval(self.timeout)
        self.timer.timeout.connect(self.threadRefresh.start)

    def __del__(self):
        self.timer.stop()
        # super().__del__()


class hexapodControl(ControlWithRefresh):

    def __init__(self, name, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self.controller = hexapod(self.name)
        self.initUI()
        self.makeConnections()
        self.timer.start()
        
    def initUI(self):
        uic.loadUi('ui/hexapod.ui', self)

        self.axes = ['x', 'y', 'z', 'alpha', 'beta', 'gamma']
        self.axesControl = {'x': {'pos': self.posX, 'set': self.setX, 'setStep': self.setStepX, 'home': self.homeX}, 
                            'y': {'pos': self.posY, 'set': self.setY, 'setStep': self.setStepY, 'home': self.homeY}, 
                            'z': {'pos': self.posZ, 'set': self.setZ, 'setStep': self.setStepZ, 'home': self.homeZ}, 
                            'alpha': {'pos': self.posAlpha, 'set': self.setAlpha, 'setStep': self.setStepAlpha, 'home': self.homeAlpha}, 
                            'beta': {'pos': self.posBeta, 'set': self.setBeta, 'setStep': self.setStepBeta, 'home': self.homeBeta}, 
                            'gamma': {'pos': self.posGamma, 'set': self.setGamma, 'setStep': self.setStepGamma, 'home': self.homeGamma}} 
           
        for axis in self.axes:
            self.axesControl[axis]['home'].clicked.connect(self.home(axis))
        
        self.buttonStop.clicked.connect(self.stopAll)
        self.buttonHomeAll.clicked.connect(self.homeAll)        
    
    def makeConnections(self):
        for axis in self.axes:
            self.axesControl[axis]['set'].valueChanged.connect(self.controller.setValue(axis))
                
    def refresh(self):
        '''
        A function that reads the machine and updates the values
        '''
                
        for axis in self.axes:
            # position needs to be read from controller
            self.axesControl[axis]['pos'].setText(str(np.round(self.axesControl[axis]['set'].value(), 3)))
            self.axesControl[axis]['set'].setSingleStep(self.axesControl[axis]['setStep'].value())
    
    def disable(self, axis):
        self.axesControl[axis]['set'].setEnabled(False)        
        self.axesControl[axis]['setStep'].setEnabled(False)
    
    def enable(self, axis):
        self.axesControl[axis]['set'].setEnabled(True)        
        self.axesControl[axis]['setStep'].setEnabled(True)
        
    def home(self, axis):
        def homeFunc():
            print('Home ', axis)
            self.disable(axis)            
            self.controller.home(axis)
            self.enable(axis)
            self.axesControl[axis]['set'].setValue(0)
        return homeFunc
        
        
    def stopAll(self):
        print('Stop all Smaract stages')
        
    def homeAll(self):
        print('Home all Smaract stages')
        for axis in self.axes:
            self.home(axis)()
        
        
class Executor(QThread):
    def __init__(self, function, parent = None):
        super(Executor, self).__init__(parent)
        self.function = function

    def run(self):
        self.function()


class ExecutorwithArg(Executor):
    def __init__(self, function, target = None, parent = None):
        super(Executor, self).__init__(parent)
        self.function = function
        self.target = target

    def run(self):
        if self.target == None:
            self.function()
        else:
            self.function(self.target)
