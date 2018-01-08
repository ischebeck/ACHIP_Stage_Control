#!/opt/gfa/python-3.5/latest/bin/python
import sys
from PyQt4.QtGui import QApplication, QInputDialog, QWidget
# from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog
from epics import PV

class App(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.bpm = createListBPM()
        self.getDouble()
        self.show()

    def getDouble(self):
        d, ok = QInputDialog.getDouble(self, 'Bpm charge threshold', 'Set charge threshold [pC]', 0.3, 0, 200, 1)
        if ok:
            print('Changing BPM threshold to %.3f pC' % d)
            setBPMThresold(self.bpm, d)
            closeBPMList(self.bpm)
        else:
            print('Aborting...')


class BPM(object):

    def __init__(self, bpmName):
        self.control = PV(bpmName + ':Q-FB-THR')

    def setThreshold(self, value):
        self.control.value = value

    def close(self):
        self.control.disconnect()


def createListBPM():
    bpm = []
    bpm.append(BPM('SINEG01-DBPM340'))
    bpm.append(BPM('SINSB01-DBPM150'))
    bpm.append(BPM('SINSB02-DBPM150'))
    bpm.append(BPM('SINLH01-DBPM060'))
    bpm.append(BPM('SINLH02-DBPM210'))
    bpm.append(BPM('SINLH02-DBPM240'))
    bpm.append(BPM('SINLH03-DBPM010'))
    bpm.append(BPM('SINLH03-DBPM050'))
    bpm.append(BPM('SINLH03-DBPM090'))
    bpm.append(BPM('SINSB03-DBPM120'))
    bpm.append(BPM('SINSB03-DBPM220'))
    bpm.append(BPM('SINSB04-DBPM120'))
    bpm.append(BPM('SINSB04-DBPM220'))
    bpm.append(BPM('SINSB05-DBPM120'))
    bpm.append(BPM('SINSB05-DBPM220'))
    bpm.append(BPM('SINXB01-DBPM120'))
    bpm.append(BPM('SINBC01-DBPM010'))
    bpm.append(BPM('SINBC01-DBPM030'))
    bpm.append(BPM('SINBC01-DBPM080'))
    bpm.append(BPM('SINBC01-DBPM100'))
    bpm.append(BPM('SINBC02-DBPM140'))
    bpm.append(BPM('SINBC02-DBPM320'))
    bpm.append(BPM('SINDI01-DBPM010'))
    bpm.append(BPM('SINDI01-DBPM060'))
    bpm.append(BPM('SINDI02-DBPM010'))
    bpm.append(BPM('SINDI02-DBPM040'))
    bpm.append(BPM('S10CB01-DBPM220'))
    bpm.append(BPM('S10CB01-DBPM420'))
    bpm.append(BPM('S10CB02-DBPM220'))
    bpm.append(BPM('S10CB02-DBPM420'))
    bpm.append(BPM('S10BD01-DBPM020'))
    bpm.append(BPM('S10CB03-DBPM220'))
    bpm.append(BPM('S10CB03-DBPM420'))
    bpm.append(BPM('S10CB04-DBPM220'))
    bpm.append(BPM('S10CB04-DBPM420'))
    bpm.append(BPM('S10CB05-DBPM220'))
    bpm.append(BPM('S10CB05-DBPM420'))
    bpm.append(BPM('S10CB06-DBPM220'))
    bpm.append(BPM('S10CB06-DBPM420'))
    bpm.append(BPM('S10CB07-DBPM220'))
    bpm.append(BPM('S10CB07-DBPM420'))
    bpm.append(BPM('S10CB08-DBPM220'))
    bpm.append(BPM('S10CB08-DBPM420'))
    bpm.append(BPM('S10CB09-DBPM220'))
    bpm.append(BPM('S10BC01-DBPM010'))
    bpm.append(BPM('S10BC01-DBPM050'))
    bpm.append(BPM('S10BC01-DBPM090'))
    bpm.append(BPM('S10BC02-DBPM140'))
    bpm.append(BPM('S10BC02-DBPM320'))
    bpm.append(BPM('S10MA01-DBPM010'))
    bpm.append(BPM('S10MA01-DBPM060'))
    bpm.append(BPM('S10MA01-DBPM120'))
    bpm.append(BPM('S20CB01-DBPM420'))
    bpm.append(BPM('S20CB02-DBPM420'))
    bpm.append(BPM('S20CB03-DBPM420'))
    bpm.append(BPM('S20SY01-DBPM010'))
    bpm.append(BPM('S20SY01-DBPM040'))
    bpm.append(BPM('S20SY01-DBPM060'))
    bpm.append(BPM('S20SY02-DBPM080'))
    bpm.append(BPM('S20SY02-DBPM120'))
    bpm.append(BPM('S20SY02-DBPM150'))
    bpm.append(BPM('S20SY03-DBPM010'))
    bpm.append(BPM('S20SY03-DBPM040'))
    bpm.append(BPM('S20SY03-DBPM080'))
    bpm.append(BPM('S30CB01-DBPM420'))
    bpm.append(BPM('S30CB02-DBPM420'))
    bpm.append(BPM('S30CB03-DBPM420'))
    bpm.append(BPM('S30CB04-DBPM420'))
    bpm.append(BPM('S30CB05-DBPM420'))
    bpm.append(BPM('S30CB06-DBPM420'))
    bpm.append(BPM('S30CB07-DBPM420'))
    bpm.append(BPM('S30CB08-DBPM420'))
    bpm.append(BPM('S30CB09-DBPM420'))
    bpm.append(BPM('S30CB10-DBPM420'))
    bpm.append(BPM('S30CB11-DBPM420'))
    bpm.append(BPM('S30CB12-DBPM420'))
    bpm.append(BPM('S30CB13-DBPM420'))
    bpm.append(BPM('S30CB14-DBPM420'))
    bpm.append(BPM('S30CB15-DBPM420'))
    bpm.append(BPM('SARCL01-DBPM010'))
    bpm.append(BPM('SARCL01-DBPM060'))
    bpm.append(BPM('SARCL01-DBPM120'))
    bpm.append(BPM('SARCL01-DBPM150'))
    bpm.append(BPM('SARCL02-DBPM110'))
    bpm.append(BPM('SARCL02-DBPM220'))
    bpm.append(BPM('SARCL02-DBPM260'))
    bpm.append(BPM('SARCL02-DBPM330'))
    bpm.append(BPM('SARCL02-DBPM470'))
    bpm.append(BPM('SARMA01-DBPM040'))
    bpm.append(BPM('SARMA01-DBPM100'))
    bpm.append(BPM('SARMA02-DBPM010'))
    bpm.append(BPM('SARMA02-DBPM020'))
    bpm.append(BPM('SARMA02-DBPM040'))
    bpm.append(BPM('SARMA02-DBPM110'))
    bpm.append(BPM('SARUN01-DBPM070'))
    bpm.append(BPM('SARUN02-DBPM070'))
    bpm.append(BPM('SARUN03-DBPM070'))
    bpm.append(BPM('SARUN04-DBPM070'))
    bpm.append(BPM('SARUN05-DBPM070'))
    bpm.append(BPM('SARUN06-DBPM070'))
    bpm.append(BPM('SARUN07-DBPM070'))
    bpm.append(BPM('SARUN08-DBPM070'))
    bpm.append(BPM('SARUN09-DBPM070'))
    bpm.append(BPM('SARUN10-DBPM070'))
    bpm.append(BPM('SARUN11-DBPM070'))
    bpm.append(BPM('SARUN12-DBPM070'))
    bpm.append(BPM('SARUN13-DBPM070'))
    bpm.append(BPM('SARUN14-DBPM070'))
    bpm.append(BPM('SARUN15-DBPM070'))
    bpm.append(BPM('SARUN16-DBPM070'))
    bpm.append(BPM('SARUN17-DBPM070'))
    bpm.append(BPM('SARUN18-DBPM070'))
    bpm.append(BPM('SARUN19-DBPM070'))
    bpm.append(BPM('SARUN20-DBPM070'))
    return bpm

def setBPMThresold(bpmlist, value):
    for bpm in bpmlist:
        bpm.setThreshold(value)

def closeBPMList(bpmlist):
    for bpm in bpmlist:
        bpm.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
