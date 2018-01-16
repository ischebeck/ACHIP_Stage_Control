# -*- coding: utf-8 -*-
import sys
usePyQt5 = True
if usePyQt5: import PyQt5.QtWidgets as QtWidgets
else: import PyQt4.Gui as QtWidgets
from otherWidgets import hexapodControl

def hexapodWindow():
   hexa = hexapodControl('hexapodNAME')

   hexa.show()

   sys.exit(app.exec_())
	
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    hexapodWindow()
