# -*- coding: utf-8 -*-
import sys
usePyQt5 = True
if usePyQt5: import PyQt5.QtWidgets as QtWidgets
else: import PyQt4.Gui as QtWidgets
from otherWidgets import hexapodControl, ECMControl
from interfaces import ECM

def openWindows(ECM):

   hexa = hexapodControl('hexapod', ECM)

   hexa.show()
   
   ECMW = ECMControl('ECM', ECM)

   ECMW.show()

   sys.exit(app.exec_())
	
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ECM = ECM()
    openWindows(ECM)
