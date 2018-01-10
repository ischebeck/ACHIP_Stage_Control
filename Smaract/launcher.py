# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from otherWidgets import hexapodControl

def hexapodWindow():
   app = QtWidgets.QApplication(sys.argv)
   hexa = hexapodControl('hexapodNAME')

   hexa.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   hexapodWindow()
