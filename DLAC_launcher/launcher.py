import sys
import os
import signal
usePyQt5 = False
if usePyQt5:
    from PyQt5.QtCore import pyqtSlot, QTimer, QEvent, QLine
    from PyQt5 import uic, Qt
    from PyQt5.QtWidgets import QMainWindow, QApplication, QDockWidget, QSpacerItem
else:
    from PyQt4.QtCore import pyqtSlot, QTimer, QEvent, QLine
    from PyQt4 import uic, Qt
    from PyQt4.QtGui import QMainWindow, QApplication, QDockWidget, QSpacerItem

import subprocess
# from functools import partial
from otherWidgets import ValveWidget, MagnetWidget, BPMWidget
from otherWidgets import QuadrupoleControl, CorrectorControl, BPMControl

#from ui.launcher_gui import Ui_MainWindow

class MainWindow(QMainWindow):

    cmd_dict = {}
    # cmd_dict['motor'] = 'cd /afs/psi.ch/intranet/SF/Diagnostics/Eugenio/DLAC_motor && ./dlac.py'
    cmd_dict['motor'] = 'cd /afs/psi.ch/intranet/SF/Diagnostics/Eugenio/DLAC_motor && ./dlac.py'
    cmd_dict['screen'] = '/sf/op/bin/screen_panel -cam=SINDI02-DLAC055 -ct=1'
    cmd_dict['filter'] = '/usr/local/bin/startDM -noMsg -macro DEVICE=SINDI02-DLAC055,IOC=SINDI02-CPCL-DLAC055,HOST=SINDI02-CWAG-DLAC055,WAGOHOST=http://sinDI02-cwag-dlac055.psi.ch,WAGOHELP=https://controls.web.psi.ch/cgi-bin/twiki/view/Main/WagoInputOutputControl,EXPMOT=S_DI_LAC_EXPERT,PROPERTY2=POS_R,PROPERTY1=POS_SP /sf/common/config/qt/DIAG_WAGO_SCREEN_EXP.ui'
    cmd_dict['vacuum'] = '/usr/local/bin/startDM -noMsg /sf/vcs/config/qt/S_VCS_SINDI02.ui'
    cmd_dict['bpm'] = 'cd scripts && ./change_bpm_threshold.py'

    maxWidgets = 3
    pid_update = 3000

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # self.setupUi(self)
        uic.loadUi('ui/launcher.ui', self)
        # connection of the buttons
        self.buttonCamera.pressed.connect(lambda: self.togglePanel('screen'))
        self.buttonMotor.pressed.connect(lambda: self.togglePanel('motor'))
        self.buttonFilter.pressed.connect(lambda: self.togglePanel('filter'))
        self.buttonVacuum.pressed.connect(lambda: self.togglePanel('vacuum'))
        self.buttonLoadLock.pressed.connect(lambda: self.togglePanel('vacuum'))
        # Connection of menu elements
        self.actionSet_BPM_threshold.triggered.connect(lambda : self.togglePanel('bpm'))
        # for testing
        self.pushButton.clicked.connect(self.addWidget)
        self.pushRemove.setVisible(False)
        self.pushButton.setVisible(False)
        # self.pushButton.setObjectName('BPM')
        # pid dictionary for keeping in memory the panels opened by the gui
        self.pid_dict = {} # dictionary for the spawned processes
        # timer to check if the instances are still open
        self.timer_pid = QTimer()
        self.timer_pid.setInterval(self.pid_update)
        self.timer_pid.timeout.connect(self.refreshPID)
        self.timer_pid.start()
        # self.timer_pid.setTimerType(Qt.)
        self.visWidgets = []
        self.visAddress = []
        # Three quads
        self.addBPM('SINDI02-DBPM010', self.container, self.layoutMain)
        self.addMagnet('SINDI02-MQUA020', self.container, self.layoutMain)
        self.addMagnet('SINDI02-MQUA030', self.container, self.layoutMain)
        self.addBPM('SINDI02-DBPM040', self.container, self.layoutMain)
        self.addMagnet('SINDI02-MQUA050', self.container, self.layoutMain)
        # Spacer
        spacer = QSpacerItem(50, 10, Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Preferred)
        self.layoutMain.addItem(spacer)
        # Three quads
        self.addMagnet('SINDI02-MQUA060', self.container, self.layoutMain)
        self.addMagnet('SINDI02-MQUA070', self.container, self.layoutMain, hasCorrector=False)
        self.addBPM('SINDI02-DBPM080', self.container, self.layoutMain)
        self.addMagnet('SINDI02-MQUA090', self.container, self.layoutMain)


    def togglePanel(self, key):
        '''
        to activate a panel depending on the button pressed.
        '''
        cmd = self.cmd_dict[key]
        if not key in self.pid_dict.keys():
            print('Spawning process %s, command %s' % (key, cmd))
            try:
                self.pid_dict[key] = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            except Exception as e:
                print('Error spawning process %s with command %s' % (key, cmd))
                print(e)
        else:
            print('Killing process %s, command %s' % (key, cmd))
            pid = self.pid_dict.pop(key).pid
            try:
                os.killpg(pid, signal.SIGTERM)
            except Exception as e:
                print('Unable to terminate process %s' % cmd)
                print(e)

    @pyqtSlot()
    def refreshPID(self):
        '''
        A function to check if the open instances are still alive
        '''
        self.pid_dict = {i:self.pid_dict[i] for i in self.pid_dict if not self.pid_dict[i].poll()}

    def addWidget(self):
        '''
        TODO: add check if widget is already visible
        '''
        reqAddress = self.sender().objectName()
        print(reqAddress)
        if reqAddress in self.visAddress:
            return
        else:
            self.visAddress.append(reqAddress)
            widget = self.addr2controlWidget(self.visAddress[-1])
            if len(self.visWidgets) >= self.maxWidgets:
                self.visWidgets[0].deleteLater()
                self.visWidgets[0] = None
                self.visWidgets.pop(0)
                self.visAddress.pop(0)
            self.visWidgets.append(QDockWidget(reqAddress, self))
            self.visWidgets[-1].setWidget(widget(reqAddress))
            self.addDockWidget(Qt.Qt.BottomDockWidgetArea, self.visWidgets[-1])
            self.visWidgets[-1].installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.Close and isinstance(source, QDockWidget)):
            print('Closing widget %s ' % source.windowTitle())
            source.deleteLater()
            for i, wid in enumerate(self.visWidgets):
                if wid == source:
                    self.visWidgets[i] = None
                    self.visWidgets.pop(i)
                    self.visAddress.pop(i)
                    break
            print('Visible widgets %s ' % str(self.visWidgets))
        return super().eventFilter(source, event)

    def __del__(self):
        self.timer_pid.stop()
        for key in self.pid_dict.keys():
            try:
                os.killpg(self.pid_dict[key].pid, signal.SIGTERM)
            except Exception as e:
                print('Failed to kill subprocess %s' % key)

    @staticmethod
    def addr2controlWidget(address):
        # select the proper widget
        if 'MQUA' in address:
            return QuadrupoleControl
        elif 'MCRX' in address or 'MCRY' in address:
            return CorrectorControl
        elif 'BPM' in address:
            return BPMControl

    def addMagnet(self, magnetName, container, containerLayout, hasCorrector=True):
        q = MagnetWidget(magnetName, hasCorrector=hasCorrector, parent=container)
        q.pushQ.pressed.connect(self.addWidget)
        if hasCorrector:
            q.pushV1.pressed.connect(self.addWidget)
            q.pushV2.pressed.connect(self.addWidget)
            q.pushH1.pressed.connect(self.addWidget)
            q.pushH2.pressed.connect(self.addWidget)
        containerLayout.addWidget(q)

    def addBPM(self, bpmName, container, containerLayout):
        b = BPMWidget(bpmName, parent=container)
        b.pushBPM.pressed.connect(self.addWidget)
        containerLayout.addWidget(b)



app = QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
