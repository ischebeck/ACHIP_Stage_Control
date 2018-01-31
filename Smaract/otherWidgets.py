usePyQt5 = True
if usePyQt5:
    from PyQt5.QtCore import pyqtSlot, QTimer, QThread, QSize
    from PyQt5 import uic, Qt
    import PyQt5.QtWidgets as QtWidgets
    from PyQt5.QtWidgets import QSizePolicy, QMessageBox
else:
    from PyQt4.QtCore import pyqtSlot, QTimer, QThread, QSize
    from PyQt4 import uic, Qt
    import PyQt4.QtGui as QtWidgets, QMessageBox
    from PyQt4.QtGui import QSizePolicy
#from axes_canvas import AxesCanvas
#from axes_limits import AxesLimits
from interfaces import hexapod, ECM, l3
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
                self.devices[name].isConnected = True
                self.devices[name].show()
            else:
                print(name, ' not found')
            
    def closeControls(self, name):
        if name in self.devices:
            self.devices[name].isConnected = False
            self.devices[name].close()
        else:
            print(name, ' not found')
            
    def send(self):
        cmd = self.input.text()
        self.ECM.sendRaw(cmd)
        self.updateOutput()
        
    def updateOutput(self):
        self.output.setText(self.ECM.ret)
              
    def addDeviceControl(self, name, dev):
        self.devices[name] = dev
            
class hexapodControl(ControlWithRefresh):

    def __init__(self, name, ECM, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self.isMoving = False
        self.controller = hexapod(self.name, ECM)
        self.isHome = False
        self.ECM = ECM
        self.axes = ['x', 'y', 'z', 'pitch', 'yaw', 'roll']
        self.axesForECM = ['z', 'x', 'y', 'roll', 'pitch', 'yaw']
        self.unitConversion = {'x': -1e-6, 'y': 1e-6, 'z': -1e-6, 'pitch': -1., 'yaw': 1., 'roll': -1.}
        self.initUI()
        self.makeConnections()
        self.timer.start()
        self.setWindowTitle('Hexapod Control')
        
        self.pos = {}
        self.posTarget = {}
        self.isConnected = False
        for axis in self.axes:
            self.pos[axis] = 'disconnected'
            self.posTarget[axis] = 0.
    
    def initUI(self):
        uic.loadUi('ui/hexapod.ui', self)
        self.axesControl = {'x': {'pos': self.posX, 'set': self.setX, 'setStep': self.setStepX, 'go': self.bGoX, 'sL': self.bXL, 'sR': self.bXR}, 
                            'y': {'pos': self.posY, 'set': self.setY, 'setStep': self.setStepY, 'go': self.bGoY, 'sL': self.bYL, 'sR': self.bYR}, 
                            'z': {'pos': self.posZ, 'set': self.setZ, 'setStep': self.setStepZ, 'go': self.bGoZ, 'sL': self.bZL, 'sR': self.bZR}, 
                            'pitch': {'pos': self.posPitch, 'set': self.setPitch, 'setStep': self.setStepPitch, 'go': self.bGoRX, 'sL': self.bRXL, 'sR': self.bRXR}, 
                            'yaw': {'pos': self.posYaw, 'set': self.setYaw, 'setStep': self.setStepYaw, 'go': self.bGoRY, 'sL': self.bRYL, 'sR': self.bRYR}, 
                            'roll': {'pos': self.posRoll, 'set': self.setRoll, 'setStep': self.setStepRoll, 'go': self.bGoRZ, 'sL': self.bRZL, 'sR': self.bRZR}} 
        
    def makeConnections(self):
        self.bStop.clicked.connect(self.stopAll)
        self.bHomeAll.clicked.connect(self.homeAll)
                
        for axis in self.axes:
            self.axesControl[axis]['setStep'].valueChanged.connect(self.axesControl[axis]['set'].setSingleStep)
            self.axesControl[axis]['go'].clicked.connect(self.goToSetPos(axis))
            self.axesControl[axis]['sL'].clicked.connect(self.makeStep(axis, -1.))
            self.axesControl[axis]['sR'].clicked.connect(self.makeStep(axis, 1.))
            
    def refresh(self): 
        if self.isConnected:
            pos = self.controller.get6d()
            self.isMoving = self.controller.isMoving()
            for i, axis in enumerate(self.axesForECM):
                self.pos[axis] = pos[i]

           
            posRounded = self.posRound()
            
            for axis in self.axes:
                self.axesControl[axis]['pos'].setText(posRounded[axis])
            if self.isMoving:
                self.labelStatus.setStyleSheet('QLabel {background: yellow}')
            else:
                self.labelStatus.setStyleSheet('QLabel {background: green}')

    def posRound(self):
        posRounded = {}
        for axis in self.axes:
            try:
                posRounded[axis] = str(np.round(float(self.pos[axis])/self.unitConversion[axis], 2))
            except:
                posRounded[axis] = self.pos[axis]
        
        return posRounded
                      
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
              
    def set6d(self): 
        pos = []
        for axis in self.axesForECM:
            pos.append(self.unitConversion[axis]*self.posTarget[axis])
        self.controller.set6d(pos)
        
    def makeStep(self, axis, sign):
        def function():
            self.posTarget[axis] += sign * self.axesControl[axis]['setStep'].value()
            self.set6d()
        return function
            
    def goToSetPos(self, axis):
        def function():
            self.posTarget[axis] = self.axesControl[axis]['set'].value()
            self.set6d()
        return function
    
    def closeEvent(self, event):
        self.isConnected = False
        event.accept()
        
class linearControl(ControlWithRefresh):

    def __init__(self, name, ECM, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self.movState = {}
        self.controller = l3(self.name, ECM)
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
                self.axesControl[axis] = {'pos': self.posX, 'set': self.setX, 'setStep': self.setStepX, 'go': self.bGoX, 'sL': self.bXL, 'sR': self.bXR, 'home': self.bHomeX, 'labelHome': self.labelHomeX, 'stop': self.bStopX} 
            if axis == 'y':     
                self.axesControl[axis] = {'pos': self.posY, 'set': self.setY, 'setStep': self.setStepY, 'go': self.bGoY, 'sL': self.bYL, 'sR': self.bYR, 'home': self.bHomeY, 'labelHome': self.labelHomeY, 'stop': self.bStopY}
            if axis == 'z':     
                self.axesControl[axis] = {'pos': self.posZ, 'set': self.setZ, 'setStep': self.setStepZ, 'go': self.bGoZ, 'sL': self.bZL, 'sR': self.bZR, 'home': self.bHomeZ, 'labelHome': self.labelHomeZ, 'stop': self.bStopZ}
            
    def makeConnections(self):
        self.bStopAll.clicked.connect(self.stopAll)
           
        for axis in self.axes:
            self.axesControl[axis]['setStep'].valueChanged.connect(self.axesControl[axis]['set'].setSingleStep)
            self.axesControl[axis]['go'].clicked.connect(self.goToSetPos(axis))
            self.axesControl[axis]['sL'].clicked.connect(self.makeStep(axis, -1.))
            self.axesControl[axis]['sR'].clicked.connect(self.makeStep(axis, 1.))
            self.axesControl[axis]['home'].clicked.connect(self.home(axis))
            self.axesControl[axis]['stop'].clicked.connect(self.stop(axis))
            
    def refresh(self): 
        if self.isConnected:
            for axis in self.axes:
                self.pos[axis] = self.controller.getPos(self.chForECM[axis])
                self.movState[axis] = self.controller.movState(self.chForECM[axis])
                self.isHome[axis] = self.controller.isHome(self.chForECM[axis])
                
            posRounded = self.posRound()
            for axis in self.axes:
                self.axesControl[axis]['pos'].setText(posRounded[axis])
                
                if self.movState[axis] == '0':
                    self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: }')                
                if self.movState[axis] == '4':
                    self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: yellow}')
                if self.movState[axis] == '7':
                    self.axesControl[axis]['pos'].setStyleSheet('QLabel {background: orange}')
                               
                if self.isHome[axis]:
                    self.axesControl[axis]['labelHome'].setStyleSheet('QLabel {background: }')
                if not self.isHome[axis]:
                    self.axesControl[axis]['labelHome'].setStyleSheet('QLabel {background: red}')
                    
    def posRound(self):
        posRounded = {}
        for axis in self.axes:
            try:
                posRounded[axis] = str(np.round(float(self.pos[axis])/self.unitConversion[axis], 2))
            except:
                posRounded[axis] = self.pos[axis]
        
        return posRounded
                    
    def home(self, axis):
        def function():
            reply = QMessageBox.question(self, 'Confirmation', 'Start Homing '+self.name+' '+axis+'?', QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                
                print('Home Smaract '+self.name+' ' + axis)
                self.controller.home(self.chForECM[axis])
    
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
        pos = self.unitConversion[axis]*self.posTarget[axis]
        self.controller.setPos(self.chForECM[axis], pos)
        
    def makeStep(self, axis, sign):
        def function():
            self.posTarget[axis] += sign * self.axesControl[axis]['setStep'].value()
            self.setPos(axis)
        return function
            
    def goToSetPos(self, axis):
        def function():
            self.posTarget[axis] = self.axesControl[axis]['set'].value()
            self.setPos(axis)
        return function
    
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