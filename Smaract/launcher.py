# -*- coding: utf-8 -*-
import sys
usePyQt5 = True
if usePyQt5: import PyQt5.QtWidgets as QtWidgets
else: import PyQt4.Gui as QtWidgets
from otherWidgets import hexapodControl, ECMControl, linearControl
from interfaces import ECM

def openWindows(ECM):
 
   ECMW = ECMControl('ECM', ECM)
   hexa = hexapodControl('hexapod', ECM)
   l1 = linearControl('l1', ECM)
   l2 = linearControl('l2', ECM)
   l3 = linearControl('l3', ECM)
   lH = linearControl('lH', ECM)
   ECMW.addDeviceControl('hexapod', hexa)
   ECMW.addDeviceControl('l1', l1)
   ECMW.addDeviceControl('l2', l2)
   ECMW.addDeviceControl('l3', l3)
   ECMW.addDeviceControl('lH', lH)
   ECMW.show()

   sys.exit(app.exec_())
	
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ECM = ECM()
    openWindows(ECM)
