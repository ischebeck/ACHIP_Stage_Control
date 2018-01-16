# PyQt5 imports
# from PyQt5 import QtWidgets, Qt, uic
# from PyQt5.QtCore import pyqtSlot, QTimer, QSize
# PyQt4 imports
from PyQt4.QtCore import pyqtSlot, QTimer, QThread, QSize
from PyQt4 import uic, Qt
import PyQt4.Gui as QtWidgets
from PyQt4.QtGui import QSizePolicy
from axes_canvas import AxesCanvas
from axes_limits import AxesLimits
from interfaces import Quadrupole, Corrector, BPM
from time import time
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

class ValveWidget(QtWidgets.QWidget):

    def __init__(self, valveName, parent=None):
        super().__init__(parent=parent)
        self.name = valveName
        grid = QtWidgets.QGridLayout()
        title = QtWidgets.QLabel(self.name, self)
        title.setAlignment(Qt.Qt.AlignCenter)
        grid.addWidget(title)
        self.setLayout(grid)

class MagnetWidget(QtWidgets.QWidget):

    def __init__(self, quadname, hasCorrector=True, parent=None):
        super().__init__(parent=parent)
        self.name = quadname
        self.hasCorrector = hasCorrector
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/magnetWidget.ui', self) # load the ui file
        # self.setupUi(self)
        self.labelName.setText(self.name)
        # set the object names to the devices. In this way it will open the right widgets
        self.pushQ.setObjectName(self.name)
        if self.hasCorrector:
            self.pushH1.setObjectName(self.quad2corrName(self.name, 'X'))
            self.pushH2.setObjectName(self.quad2corrName(self.name, 'X'))
            self.pushV1.setObjectName(self.quad2corrName(self.name, 'Y'))
            self.pushV2.setObjectName(self.quad2corrName(self.name, 'Y'))
        else:
            self.pushH1.setVisible(False); #self.labelH1.setVisible(False)
            self.pushH2.setVisible(False); #self.labelH2.setVisible(False)
            self.pushV1.setVisible(False); #self.labelV1.setVisible(False)
            self.pushV2.setVisible(False); #self.labelV2.setVisible(False)

    @staticmethod
    def quad2corrName(quadname, direction):
        identifier = 'MQUA'
        idx = quadname.find(identifier)
        if idx:
            return quadname[:idx] + 'MCR' + direction.upper() + quadname[idx+len(identifier):]
        else:
            print('Invalid quadrupole identifier')
            return None

class BPMWidget(QtWidgets.QWidget):

    def __init__(self, bpmName, parent=None):
        super().__init__(parent=parent)
        self.name = bpmName
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/bpmWidget.ui', self) # load the ui file
        # self.setupUi(self)
        self.labelName.setText(self.name)
        # set the object names to the devices. In this way it will open the right widgets
        self.pushBPM.setObjectName(self.name)


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


class QuadrupoleControl(ControlWithRefresh):

    att_spinI = {'ndec': 3, 'step': 0.01, 'range': [-10, 10], 'suffix': ' A'}
    att_spinB = {'ndec': 3, 'step': 0.001, 'range': [-10, 10], 'suffix': ' T/m'}
    att_spinE = {'ndec': 3, 'step': 1.0, 'range': [0, 5000], 'suffix': ' MeV'}

    def __init__(self, quadName, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = quadName
        self.controller = Quadrupole(self.name)
        self.initUI()
        self.makeConnections()
        self.timer.start()

    def makeConnections(self):
        self.spinI.valueChanged.connect(self.controller.setI)
        self.spinB.valueChanged.connect(self.controller.setB)
        self.spinE.valueChanged.connect(self.controller.setE)

    def initUI(self):
        uic.loadUi('ui/quadrupoleControl.ui', self)
        # Current
        init_spinbox(self.spinI, self.att_spinI)
        val = self.controller.I
        self.spinI.setValue(val)
        # Field
        init_spinbox(self.spinB, self.att_spinB)
        val = self.controller.B
        self.spinB.setValue(val)
        # Energy
        init_spinbox(self.spinE, self.att_spinE)
        val = self.controller.energy
        self.spinE.setValue(val)

    def refresh(self):
        '''
        A function that reads the machine and updates the values
        '''
        self.readI.setText(('%.' + str(self.att_spinI['ndec']) + 'f') % self.controller.I)
        self.readB.setText(('%.' + str(self.att_spinB['ndec']) + 'f') % self.controller.B)
        self.readE.setText(('%.' + str(self.att_spinE['ndec']) + 'f') % self.controller.energy)
        # print('Current %.3f' % self.controller.I)

class CorrectorControl(ControlWithRefresh):

    att_spinI = {'ndec': 3, 'step': 0.01, 'range': [-10, 10], 'suffix': ' A'}

    def __init__(self, corrName, refresh=500, parent=None):
        super().__init__(parent=parent)
        self.name = corrName
        self.controller = Corrector(self.name)
        self.initUI()
        self.makeConnections()
        self.timer.start()

    def makeConnections(self):
        self.spinI.valueChanged.connect(self.controller.setI)

    def initUI(self):
        uic.loadUi('ui/quadrupoleControl.ui', self)
        # Clean the UI
        self.spinB.deleteLater(); self.spinB = None
        self.spinE.deleteLater(); self.spinE = None
        self.readB.deleteLater(); self.readB = None
        self.readE.deleteLater(); self.readE = None
        self.labelB.deleteLater(); self.labelB = None
        self.labelE.deleteLater(); self.labelE = None
        # Current
        init_spinbox(self.spinI, self.att_spinI)
        val = self.controller.I
        self.spinI.setValue(val)

    def refresh(self):
        '''
        A function that reads the machine and updates the values
        '''
        self.readI.setText(('%.' + str(self.att_spinI['ndec']) + 'f') % self.controller.I)

class BPMControl(ControlWithRefresh):

    def __init__(self, bpmName, refresh=1000, parent=None):
        super().__init__(parent=parent)
        self.name = bpmName
        self.controller = BPM(self.name)
        self.initUI()
        self.timer.start()

    def initUI(self):
        uic.loadUi('ui/bpmControl.ui', self)
        self.canvas = AxesCanvas(
            padding_left=2,
            padding_above=7,
            padding_below=16)
        self.figure = self.canvas.figure
        self.axes = self.canvas.axes
        self.axes_limits = AxesLimits()
        self.axes.set_aspect('equal', adjustable='box')
        self.containerLayout.addWidget(self.canvas)
        x, y, q = self.controller.readFull()
        self.charge.setText('Q = %.3f pC' % q)
        self.spot,  = self.axes.plot(x, y, marker='o', markersize=10)
        self.axes.grid(True)
        self.axes_limits.force_change()

    def refresh(self):
        # t0 = time()
        x, y, q = self.controller.readFull()
        xmin, xmax = self.computeMinMax(x)
        ymin, ymax = self.computeMinMax(y)

        self.spot.set_data(x, y)
        self.axes_limits.set_limits(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        # print('x: %.3f --- y: %.3f' % (x, y))
        # print('limits x: %.3f %.3f' % (xmin, xmax))
        # print('limits y: %.3f %.3f' % (ymin, ymax))
        if self.axes_limits.changed():
            self.axes_limits.set_on_axes(self.axes)
            # self.axes.set_aspect('equal', adjustable='box')
            self.canvas.draw()
            # print('Limits changed')
        else:
            self.axes.draw_artist(self.axes.patch)
            #for spine in self.axes.spines.itervalues():
            #    self.axes.draw_artist(spine)
            for line in self.axes.get_xgridlines()[1:-1]:
                self.axes.draw_artist(line)
            for line in self.axes.get_ygridlines()[1:-1]:
                self.axes.draw_artist(line)
            for line in self.axes.get_xticklines()[1:-1]:
                self.axes.draw_artist(line)
            for line in self.axes.get_yticklines()[1:-1]:
                self.axes.draw_artist(line)
            self.axes.draw_artist(self.spot)
            self.canvas.blit(self.axes.bbox)

        self.charge.setText('Q = %.3f pC' % q)
        self.position.setText('X = %.3f mm --- Y = %.3f mm' % (x, y))
        # print('Updating took %.5f s' % abs(t0 - time()))

    @staticmethod
    def computeMinMax(val):
        if val < 0.5:
            minVal = -0.5; maxVal = 0.5
        else:
            minVal = -1. * np.ceil(abs(val))
            maxVal = abs(minVal)
        return minVal, maxVal



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
