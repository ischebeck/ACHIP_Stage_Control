usePyQt5 = True
if usePyQt5:
    from PyQt5.QtCore import pyqtSlot, QTimer, QThread, QSize
    from PyQt5 import uic, Qt
    import PyQt5.QtWidgets as QtWidgets
    from PyQt5.QtWidgets import QSizePolicy
else:
    from PyQt4.QtCore import pyqtSlot, QTimer, QThread, QSize
    from PyQt4 import uic, Qt
    import PyQt4.QtGui as QtWidgets
    from PyQt4.QtGui import QSizePolicy
#from axes_canvas import AxesCanvas
#from axes_limits import AxesLimits
from interfaces import hexapod, ECM
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

class ECMControl(ControlWithRefresh):

    def __init__(self, name, ECM, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.ECM = ECM
        self.isConnected = False
        self.initUI()
        self.makeConnections()
        self.timer.start()
        self.setWindowTitle('ECM Control')
        
    def initUI(self):
        uic.loadUi('ui/ECM.ui', self)

        self.buttonConnect.clicked.connect(self.connect)
        self.buttonDisconnect.clicked.connect(self.disconnect)
        self.buttonSend.clicked.connect(self.send)
        
    def makeConnections(self):
        return 

    def refresh(self):
        '''
        A function that reads the machine and updates the values
        '''
        return 
                        
    def connect(self):
        isConnected = self.ECM.connect()
        if isConnected:
            self.buttonConnect.setStyleSheet('QPushButton {background: green}')         
            
    def disconnect(self):
        self.ECM.disconnect()
        self.isConnected = False
        
        self.buttonConnect.setStyleSheet('QPushButton {background: }')

    def send(self):
        cmd = self.input.text()
        self.ECM.sendRaw(cmd)
        self.updateOutput()
        
    def updateOutput(self):
        self.output.setText(self.ECM.ret)
      
        
        
class hexapodControl(ControlWithRefresh):

    def __init__(self, name, ECM, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self.isConnected = False
        self.isHome = False
        self.isMoving = {'x': False, 'y': False, 'z': False, 'pitch': False, 'yaw': False, 'roll': False}
        self.controller = hexapod(self.name, ECM)
        self.ECM = ECM
        self.initUI()
        self.makeConnections()
        self.timer.start()
        self.setWindowTitle('Hexapod Control')
        self.unitConversion = {'x': 1e-6, 'y': 1e-6, 'z': 1e-6, 'pitch': 1., 'yaw': 1., 'roll': 1.}
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        self.axesForECM = ['z', 'x', 'y', 'roll', 'pitch', 'yaw']
        
    def initUI(self):
        uic.loadUi('ui/hexapod.ui', self)
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        self.axesForECM = ['z', 'x', 'y', 'roll', 'pitch', 'yaw']
        self.axesControl = {'x': {'pos': self.posX, 'set': self.setX, 'setStep': self.setStepX}, 
                            'y': {'pos': self.posY, 'set': self.setY, 'setStep': self.setStepY}, 
                            'z': {'pos': self.posZ, 'set': self.setZ, 'setStep': self.setStepZ}, 
                            'pitch': {'pos': self.posPitch, 'set': self.setPitch, 'setStep': self.setStepPitch}, 
                            'yaw': {'pos': self.posYaw, 'set': self.setYaw, 'setStep': self.setStepYaw}, 
                            'roll': {'pos': self.posRoll, 'set': self.setRoll, 'setStep': self.setStepRoll}} 
           
        self.disableControl()
        self.buttonConnect.clicked.connect(self.connect)
        self.buttonDisconnect.clicked.connect(self.disconnect)
        self.buttonStop.clicked.connect(self.stopAll)
        self.buttonHomeAll.clicked.connect(self.homeAll)        
    
    def makeConnections(self):
        for axis in self.axes:
            self.axesControl[axis]['setStep'].valueChanged.connect(self.axesControl[axis]['set'].setSingleStep)
            self.axesControl[axis]['set'].valueChanged.connect(self.set6d(axis))
            
    def refresh(self):         
        for axis in self.axes:
            if self.isMoving[axis]:
                self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: orange}')
            else:
                self.axesControl[axis]['pos'].setStyleSheet('QLabel {background:}')
                
    def connect(self):
        if self.ECM.isConnected:
            self.isConnected = self.controller.connect()
            if self.isConnected:
                self.buttonConnect.setStyleSheet('QPushButton {background: green}')         
            
            self.isHome = self.controller.isHome()
            if self.isHome:
                self.buttonHomeAll.setStyleSheet('QPushButton {background: green}')         
            
            self.enableControl()
        
    def disconnect(self):
        self.controller.disconnect()
        self.isConnected = False
        self.isHome = False
        
        for axis in self.axes:    
            self.axesControl[axis]['pos'].setText('not connected')
        
        self.disableControl()
        self.buttonHomeAll.setStyleSheet('QPushButton {background: }')     
        self.buttonConnect.setStyleSheet('QPushButton {background: }')       
    
    def stopAll(self):
        print('Stop all Smaract Hexapod stages')
        self.controller.stopAll()
        
        self.disconnect()
    
    def homeAll(self):
        print('Home all Smaract Hexapod stages')
        success = self.controller.home()
        self.waitMovement('all')
        if success:
            self.buttonHomeAll.setStyleSheet('QPushButton {background: green}')
        else:
            self.buttonHomeAll.setStyleSheet('QPushButton {background: red}')
    
    def waitMovement(self, axis):
        if axis == 'all':
            for a in self.axes:
                self.isMoving[a] = True
        else:        
            self.isMoving[axis] = True
        
        self.disableControl()
        while self.controller.isMoving():
            #get pos and update 
            sleep(0.1)
        
        if axis == 'all':
            for a in self.axes:
                self.isMoving[a] = False
        else:        
            self.isMoving[axis] = False
        
        self.enableControl()
        
    def disableControl(self):
        for axis in self.axes:
            self.axesControl[axis]['set'].setEnabled(False)        
            self.axesControl[axis]['setStep'].setEnabled(False)
    
    def enableControl(self):
        for axis in self.axes:
            self.axesControl[axis]['set'].setEnabled(True)        
            self.axesControl[axis]['setStep'].setEnabled(True)
      
    def set6d(self, axis): 
        def function(value):
            pos = []
            for axis in self.axesForECM:
                pos.append(self.unitConversion[axis]*self.axesControl[axis]['set'].value())
            self.controller.set6d(pos)
            self.waitMovement(axis)
        return function
        
        
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