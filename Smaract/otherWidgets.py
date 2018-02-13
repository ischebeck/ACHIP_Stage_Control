usePyQt5 = True
if usePyQt5:
    from PyQt5.QtCore import pyqtSlot, QTimer, QThread, QSize
    from PyQt5 import uic, Qt
    import PyQt5.QtWidgets as QtWidgets
    from PyQt5.QtWidgets import QSizePolicy, QMessageBox, QInputDialog, QLineEdit
else:
    from PyQt4.QtCore import pyqtSlot, QTimer, QThread, QSize
    from PyQt4 import uic, Qt
    import PyQt4.QtGui as QtWidgets
    from PyQt4.QtGui import QSizePolicy, QMessageBox, QInputDialog, QLineEdit
#from axes_canvas import AxesCanvas
#from axes_limits import AxesLimits
from interfaces import hexapod, ECM, smaractLinear
from time import time, sleep
import numpy as np
from storage import *

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

    def __init__(self, refresh=2000, parent=None):
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
        self.devices = {}
        
    def initUI(self):
        uic.loadUi('ui/ECM.ui', self)

    def makeConnections(self):
        self.bConnect.clicked.connect(self.connect)
        self.bDisconnect.clicked.connect(self.disconnect)
        self.bSend.clicked.connect(self.send)
        self.bLoad.clicked.connect(lambda: self.load(path=''))
        self.bSave.clicked.connect(lambda: self.save(path=''))
        self.bSetAll.clicked.connect(self.setAll)
        self.bStartHexapod.clicked.connect(lambda: self.openControls('hexapod'))
        self.bCloseHexapod.clicked.connect(lambda: self.closeControls('hexapod'))
        self.bStartL1.clicked.connect(lambda: self.openControls('l1'))
        self.bCloseL1.clicked.connect(lambda: self.closeControls('l1'))
        self.bStartL2.clicked.connect(lambda: self.openControls('l2'))
        self.bCloseL2.clicked.connect(lambda: self.closeControls('l2'))
        self.bStartL3.clicked.connect(lambda: self.openControls('l3'))
        self.bCloseL3.clicked.connect(lambda: self.closeControls('l3'))
        self.bStartLH.clicked.connect(lambda: self.openControls('lH'))
        self.bCloseLH.clicked.connect(lambda: self.closeControls('lH'))
        return 

    def refresh(self):
        '''
        A function that reads the machine and updates the values
        '''
        return 
                        
    def connect(self):
        self.isConnected = self.ECM.connect()
        if self.isConnected:
            print('ECM connected.')
            self.bConnect.setStyleSheet('QPushButton {background: green}')         

    def disconnect(self):
        for dev in self.devices:
            self.closeControls(dev)
            
        self.ECM.disconnect()
        self.isConnected = False
        print('ECM disconnected.')
        self.bConnect.setStyleSheet('QPushButton {background: }')    

    def openControls(self, name):
        if self.isConnected:
            if name in self.devices:
                self.closeAllControls()
                self.devices[name].isConnected = True
                self.devices[name].settings()
                self.devices[name].show()
            else:
                print(name, ' not found')
            
    def closeControls(self, name):
        if name in self.devices:
            self.devices[name].isConnected = False
            self.devices[name].close()
        else:
            print(name, ' not found')
            
    def closeAllControls(self):
        for name in self.devices:
            if self.devices[name].isConnected:
                self.closeControls(name)
                
    def send(self):
        cmd = self.input.text()
        self.ECM.sendRaw(cmd)
        self.updateOutput()
        
    def updateOutput(self):
        self.output.setText(self.ECM.ret)
              
    def addDeviceControl(self, name, dev):
        self.devices[name] = dev
    
    def save(self, path = ''):
        if path == '':
            path = getFileSave()
        if path != '':
            for name in self.devices:
                self.devices[name].save(path = path)

    def load(self, path = ''):
        if path == '':
            path = getFileOpen()
        if path != '':
            for name in self.devices:
                self.devices[name].load(path = path)
            
    def setAll(self):
        for name in self.devices:
            self.devices[name].setAll()
                
    def closeEvent(self, event):
        self.disconnect()
        event.accept()
            
class hexapodControl(ControlWithRefresh):

    def __init__(self, name, ECM, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self.isMoving = False
        self.controller = hexapod(self.name, ECM)
        self.isHome = False
        self.ECM = ECM
        self.axes = ['x', 'y', 'z', 'rx', 'ry', 'rz']
        self.axesForECM = ['z', 'x', 'y', 'rz', 'rx', 'ry']
        self.unitConversion = {'x': -1e-6, 'y': 1e-6, 'z': -1e-6, 'rx': -1., 'ry': 1., 'rz': -1.}
        self.initUI()
        self.makeConnections()
        self.timer.start()
        self.setWindowTitle('Hexapod Control')
        
        self.pos = {}
        self.piv = {}
        self.posTarget = {}
        self.isConnected = False
        for axis in self.axes:
            self.pos[axis] = None
            self.posTarget[axis] = 0.
    
    def initUI(self):
        uic.loadUi('ui/hexapod.ui', self)
        self.axesControl = {'x': {'pos': self.posX, 'set': self.setX, 'setStep': self.setStepX, 'go': self.bGoX, 'sL': self.bXL, 'sR': self.bXR, 'piv': self.pivotX}, 
                            'y': {'pos': self.posY, 'set': self.setY, 'setStep': self.setStepY, 'go': self.bGoY, 'sL': self.bYL, 'sR': self.bYR, 'piv': self.pivotY}, 
                            'z': {'pos': self.posZ, 'set': self.setZ, 'setStep': self.setStepZ, 'go': self.bGoZ, 'sL': self.bZL, 'sR': self.bZR, 'piv': self.pivotZ}, 
                            'rx': {'pos': self.posRX, 'set': self.setRX, 'setStep': self.setStepRX, 'go': self.bGoRX, 'sL': self.bRXL, 'sR': self.bRXR}, 
                            'ry': {'pos': self.posRY, 'set': self.setRY, 'setStep': self.setStepRY, 'go': self.bGoRY, 'sL': self.bRYL, 'sR': self.bRYR}, 
                            'rz': {'pos': self.posRZ, 'set': self.setRZ, 'setStep': self.setStepRZ, 'go': self.bGoRZ, 'sL': self.bRZL, 'sR': self.bRZR}} 
        
    def makeConnections(self):
        self.bStop.clicked.connect(self.stopAll)
        self.bHomeAll.clicked.connect(self.homeAll)
        self.bLoad.clicked.connect(lambda: self.load(path=''))
        self.bSave.clicked.connect(lambda: self.save(path=''))
        self.bSetPivot.clicked.connect(self.setPivot)    
        self.bSetAll.clicked.connect(self.setAll)
        
        for axis in self.axes:
            self.axesControl[axis]['setStep'].valueChanged.connect(self.axesControl[axis]['set'].setSingleStep)
            self.axesControl[axis]['go'].clicked.connect(self.goToSetPos(axis))
            self.axesControl[axis]['sL'].clicked.connect(self.makeStep(axis, -1.))
            self.axesControl[axis]['sR'].clicked.connect(self.makeStep(axis, 1.))
            
    def readValues(self):
        self.isMoving = self.controller.isMoving()
        self.isHome = self.controller.isHome()
        self.get6d()
          
    def refresh(self): 
        if self.isConnected:
            self.readValues()
            posRounded = self.posRound(self.pos)
            
            for axis in self.axes:
                self.axesControl[axis]['pos'].setText(posRounded[axis])
            if self.isMoving:
                self.labelStatus.setStyleSheet('QLabel {background: yellow}')
            else:
                self.labelStatus.setStyleSheet('QLabel {background: green}')
                
            if self.isHome:
                self.bHomeAll.setStyleSheet('QPushButton {background: }')
            if not self.isHome:
                self.bHomeAll.setStyleSheet('QPushButton {background: red}')
    
    def posRound(self, pos):
        posRounded = {}
        for axis in pos:
            try:
                posRounded[axis] = str(np.round(float(pos[axis])/self.unitConversion[axis], 2))
            except:
                posRounded[axis] = pos[axis]
        
        return posRounded

    def settings(self): 
        self.controller.setFrq(self.controller.stdFrq)
        pivRounded = self.getPivot()
        for axis in self.axes[:3]:
            self.axesControl[axis]['piv'].setValue(float(pivRounded[axis]))
                       
    def stopAll(self):
        print('Stop all Smaract Hexapod stages')
        try:
            self.controller.stopAll()
        except:
            print('Could not stop Hexapod. Check connection!')
            
    def homeAll(self):
        reply = QMessageBox.question(self, 'Confirmation', 'Start Homing?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            
            print('Home all Smaract Hexapod stages')
            success = self.controller.home()
            if success:
                self.bHomeAll.setStyleSheet('QPushButton {background:}')
            else:
                self.bHomeAll.setStyleSheet('QPushButton {background: red}')
              
    def get6d(self):
        posRead = self.controller.get6d()
        for i, axis in enumerate(self.axesForECM):
            self.pos[axis] = posRead[i]
            
    def set6d(self): 
        pos = []
        for axis in self.axesForECM:
            pos.append(self.unitConversion[axis]*self.posTarget[axis])
        self.controller.set6d(pos)
        
    def makeStep(self, axis, sign):
        def function():
            self.posTarget[axis] = float(self.pos[axis])/self.unitConversion[axis] + sign * self.axesControl[axis]['setStep'].value()
            self.set6d()
        return function
            
    def goToSetPos(self, axis):
        def function():
            self.posTarget[axis] = self.axesControl[axis]['set'].value()
            self.set6d()
        return function

    def getPivot(self):
        pivRead = self.controller.getPivot()
        for i, axis in enumerate(self.axesForECM[:3]):
            self.piv[axis] = pivRead[i]
        return self.posRound(self.piv)  
    
    def setPivot(self):
        pivECM = []
        for axis in self.axesForECM[:3]:
            pivECM.append(self.axesControl[axis]['piv'].value() * self.unitConversion[axis])
        success = self.controller.setPivot(pivECM)
        if success:
            print('Pivot set.')

    def setAll(self):
        self.setPivot()
        for axis in self.axes:
            self.goToSetPos(axis)()
                   
    def save(self, path = ''):
        if path == '':
            path = getFileSave()
        if path != '':
            s = Storage(path, 'test')
            self.getPivot()
            self.readValues()
            for axis in self.axes:
                if self.pos[axis] != None: 
                    s.addData(self.name, axis, float(self.pos[axis])/self.unitConversion[axis], unit = 'um')
            for axis in self.axes[:3]:
                if self.piv[axis] != None: 
                    s.addData(self.name, 'piv'+axis, float(self.piv[axis])/self.unitConversion[axis], unit = 'um')
            s.close()
            
    def load(self, path = ''):
        if path == '':
            path = getFileOpen()
        if path != '':
            s = StorageRead(path)
            for axis in self.axes:
                val = s.getData(self.name, axis)
                if val != None:
                    self.axesControl[axis]['set'].setValue(val)
            for axis in self.axes[:3]:
                piv = s.getData(self.name, 'piv'+axis)
                if piv != None:
                    self.axesControl[axis]['piv'].setValue(piv)
            s.close()
    
    def closeEvent(self, event):
        self.isConnected = False
        event.accept()
        
class linearControl(ControlWithRefresh):

    def __init__(self, name, ECM, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self.movState = {}
        self.controller = smaractLinear(self.name, ECM)
        self.isHome = {}
        self.ECM = ECM
        if name == 'l1':
            self.axes = ['z']
            self.chForECM = {'z': 8}
            self.unitConversion = {'z': 1e-6}
        if name == 'l2':
            self.axes = ['x', 'z']
            self.chForECM = {'x': 6, 'z': 7}
            self.unitConversion = {'x': -1e-6, 'z': 1e-6}
        if name == 'l3':
            self.axes = ['x', 'y', 'z']
            self.chForECM = {'x': 1, 'y': 2, 'z': 0}
            self.unitConversion = {'x': -1e-6, 'y': 1e-6, 'z': 1e-6}
        if name == 'lH':
            self.axes = ['v']
            self.chForECM = {'v': 3}
            self.unitConversion = {'v': 1e-6}
        self.initUI()
        self.makeConnections()
        self.timer.start()
        self.setWindowTitle(name)
        self.pos = {}
        self.posTarget = {}
        self.isConnected = False
        for axis in self.axes:
            self.movState[axis] = False
            self.isHome[axis] = False
            self.pos[axis] = 'disconnected'
            self.posTarget[axis] = 0.
    
    def initUI(self):
        uic.loadUi('ui/'+'l3'+'.ui', self)
        self.axesControl = {}
        for axis in self.axes:
            if axis == 'x' or axis == 'v' : 
                self.axesControl[axis] = {'pos': self.posX, 'set': self.setX, 'setStep': self.setStepX, 'go': self.bGoX, 'sL': self.bXL, 'sR': self.bXR, 'home': self.bHomeX, 'stop': self.bStopX} 
            if axis == 'y':     
                self.axesControl[axis] = {'pos': self.posY, 'set': self.setY, 'setStep': self.setStepY, 'go': self.bGoY, 'sL': self.bYL, 'sR': self.bYR, 'home': self.bHomeY, 'stop': self.bStopY}
            if axis == 'z':     
                self.axesControl[axis] = {'pos': self.posZ, 'set': self.setZ, 'setStep': self.setStepZ, 'go': self.bGoZ, 'sL': self.bZL, 'sR': self.bZR, 'home': self.bHomeZ, 'stop': self.bStopZ}
            
    def makeConnections(self):
        self.bStopAll.clicked.connect(self.stopAll)
        self.bLoad.clicked.connect(lambda: self.load(path=''))
        self.bSave.clicked.connect(lambda: self.save(path=''))
        self.bSetAll.clicked.connect(self.setAll)
        for axis in self.axes:
            self.axesControl[axis]['setStep'].valueChanged.connect(self.axesControl[axis]['set'].setSingleStep)
            self.axesControl[axis]['go'].clicked.connect(self.goToSetPos(axis))
            self.axesControl[axis]['sL'].clicked.connect(self.makeStep(axis, -1.))
            self.axesControl[axis]['sR'].clicked.connect(self.makeStep(axis, 1.))
            self.axesControl[axis]['home'].clicked.connect(self.home(axis))
            self.axesControl[axis]['stop'].clicked.connect(self.stop(axis))
    
    def readValues(self):
        for axis in self.axes:
            self.pos[axis] = self.controller.getPos(self.chForECM[axis])
            self.movState[axis] = self.controller.movState(self.chForECM[axis])
            self.isHome[axis] = self.controller.isHome(self.chForECM[axis])
    
    def refresh(self): 
        if self.isConnected:
            self.readValues()                
            posRounded = self.posRound(self.pos)
            for axis in self.axes:
                
                self.axesControl[axis]['pos'].setText(posRounded[axis])
                posDiff = abs(float(self.posTarget[axis]) - float(posRounded[axis]))
                
                if self.movState[axis] == '3': #holding
                    if posDiff >= 0.01:
                        self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: yellow}')    
                    if posDiff < 0.01:
                        self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: }')    
                
                if self.movState[axis] == '0': #stopped
                    self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: red}')
                if self.movState[axis] == '7': #homing
                    self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: orange}')
                               
                if self.isHome[axis]:
                    self.axesControl[axis]['home'].setStyleSheet('QPushButton {background: }')
                if not self.isHome[axis]:
                    self.axesControl[axis]['home'].setStyleSheet('QPushButton {background: red}')
                    
    def posRound(self, pos):
        posRounded = {}
        for axis in self.axes:
            try:
                posRounded[axis] = str(np.round(float(pos[axis])/self.unitConversion[axis], 2))
            except:
                posRounded[axis] = pos[axis]
        
        return posRounded
    
    def settings(self): 
        for ch in self.chForECM:
            self.controller.setFrq(ch, self.controller.stdFrq)  
            
    def home(self, axis):
        def function():
            reply = QMessageBox.question(self, 'Confirmation', 'Start Homing '+self.name+' '+axis+'?', QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                
                print('Home Smaract '+self.name+' ' + axis)
                if axis == 'z':
                    self.controller.home(self.chForECM[axis], autoZero = False)
                else:
                    self.controller.home(self.chForECM[axis], autoZero = True)
        return function
        
    def stop(self, axis):
        def function():
            print('Stop Smaract '+self.name+' ' + axis)
            self.controller.stop(self.chForECM[axis])
        return function

    def stopAll(self):
        print('Stop all Smaract '+self.name+' stages')
        for axis in self.axes:
            try:
                self.stop(axis)()
            except:
                print('Could not stop '+self.name+' '+axis+'. Check connection!')
    
    def setPos(self, axis): 
        self.controller.setPos(self.chForECM[axis], self.unitConversion[axis]*self.posTarget[axis])
        
    def makeStep(self, axis, sign):
        def function():
            self.posTarget[axis] = float(self.pos[axis])/self.unitConversion[axis] + sign * self.axesControl[axis]['setStep'].value()
            self.setPos(axis)
        return function
            
    def goToSetPos(self, axis):
        def function():
            self.posTarget[axis] = self.axesControl[axis]['set'].value()
            self.setPos(axis)
        return function
    
    def setAll(self):
        for axis in self.axes:
            self.goToSetPos(axis)()
    
    def save(self, path = ''):
        if path == '':
            path = getFileSave()
        if path != '':
            s = Storage(path, 'test')
            self.readValues()
            for axis in self.axes:
                if self.pos[axis] != None:
                    s.addData(self.name, axis, float(self.pos[axis])/self.unitConversion[axis], unit = 'um')            
            s.close()
            
    def load(self, path = ''):
        if path == '':
            path = getFileOpen()
        if path != '':
            s = StorageRead(path)
            for axis in self.axes:
                val = s.getData(self.name, axis)
                if val != None:
                    self.axesControl[axis]['set'].setValue(val)
            s.close()
    
    def closeEvent(self, event):
        self.isConnected = False
        event.accept()

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