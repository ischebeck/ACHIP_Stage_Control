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


class hexapodControl(ControlWithRefresh):

    def __init__(self, name, ECM, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self.isConnected = False
        self.isHome = {}
        self.controller = hexapod(self.name, ECM)
        self.initUI()
        self.makeConnections()
        self.timer.start()
        self.setWindowTitle('Hexapod Control')
        
    def initUI(self):
        uic.loadUi('ui/hexapod.ui', self)

        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        self.axesControl = {'x': {'pos': self.posX, 'set': self.setX, 'setStep': self.setStepX, 'home': self.homeX}, 
                            'y': {'pos': self.posY, 'set': self.setY, 'setStep': self.setStepY, 'home': self.homeY}, 
                            'z': {'pos': self.posZ, 'set': self.setZ, 'setStep': self.setStepZ, 'home': self.homeZ}, 
                            'pitch': {'pos': self.posPitch, 'set': self.setPitch, 'setStep': self.setStepPitch, 'home': self.homePitch}, 
                            'yaw': {'pos': self.posYaw, 'set': self.setYaw, 'setStep': self.setStepYaw, 'home': self.homeYaw}, 
                            'roll': {'pos': self.posRoll, 'set': self.setRoll, 'setStep': self.setStepRoll, 'home': self.homeRoll}} 
           
        for axis in self.axes:
            self.isHome[axis] = False
            self.axesControl[axis]['home'].clicked.connect(self.home(axis))
        
        self.buttonConnect.clicked.connect(self.connect)
        self.buttonDisconnect.clicked.connect(self.disconnect)
        self.buttonStop.clicked.connect(self.stopAll)
        self.buttonHomeAll.clicked.connect(self.homeAll)        
    
    def makeConnections(self):
        for axis in self.axes:
            self.axesControl[axis]['setStep'].valueChanged.connect(self.axesControl[axis]['set'].setSingleStep)
            self.axesControl[axis]['set'].valueChanged.connect(self.set6d())
            
    def refresh(self):
        '''
        A function that reads the machine and updates the values
        '''
                
        for axis in self.axes:
            
            if self.isConnected:
                # position needs to be read from controller
                self.axesControl[axis]['pos'].setText(str(np.round(self.axesControl[axis]['set'].value(), 3)))
                pass
            if self.controller.isMoving(axis):
                self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: orange}')
            else:
                self.axesControl[axis]['pos'].setStyleSheet('QLabel {background:}')
                
    def connect(self):
        isConnected = self.controller.connect()
        if isConnected:
            self.buttonConnect.setStyleSheet('QPushButton {background: green}')         
            
    def disconnect(self):
        self.controller.disconnect()
        self.isConnected = False
        for axis in self.axes:
            self.isHome[axis] = False
            self.axesControl[axis]['home'].setStyleSheet('QPushButton {background: }')
            self.axesControl[axis]['pos'].setText('not connected')
            
        self.buttonHomeAll.setStyleSheet('QPushButton {background: }')     
        self.buttonConnect.setStyleSheet('QPushButton {background: }')       
    
    def disable(self, axis):
        self.axesControl[axis]['set'].setEnabled(False)        
        self.axesControl[axis]['setStep'].setEnabled(False)
    
    def enable(self, axis):
        self.axesControl[axis]['set'].setEnabled(True)        
        self.axesControl[axis]['setStep'].setEnabled(True)
      
    def set6d(self):
        def function(value):
            pos = []
            for axis in self.axes:
                pos.append(self.axesControl[axis]['set'].value())
            self.controller.set6d(pos)
        return function
        
    def home(self, axis):
        def homeFunc():
            if self.isConnected[axis]:
                print('Home Hexapod ', axis)
                self.disable(axis)            
                self.isHome[axis] = self.controller.home(axis)
                self.enable(axis)
                if self.isHome[axis]:
                    self.axesControl[axis]['set'].setValue(0)
                    self.axesControl[axis]['home'].setStyleSheet('QPushButton {background: green}')
        return homeFunc
        
        
    def stopAll(self):
        print('Stop all Smaract Hexapod stages')
        self.controller.stopAll()
        self.disconnect()
        
    def homeAll(self):
        print('Home all Smaract Hexapod stages')
        isHomeList = []
        for axis in self.axes:
            self.home(axis)()
            isHomeList.append(self.isHome[axis])
        if all(isHomeList):
            self.buttonHomeAll.setStyleSheet('QPushButton {background: green}')
        
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
