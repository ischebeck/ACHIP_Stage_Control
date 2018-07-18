# -*- coding: utf-8 -*-
import h5py
import sys
import os
from os.path import join
from time import strftime, localtime
import cmd
import numpy as np
usePyQt5 = False
if usePyQt5: 
    from PyQt5.QtWidgets import QFileDialog
else:
    from PyQt4.QtGui import QFileDialog
def getFileSave():
    return QFileDialog.getSaveFileName(None, 'Select Folder', os.getcwd(), options = QFileDialog.DontConfirmOverwrite)[0]
   
def getFileOpen():
    return QFileDialog.getOpenFileName(None, 'Select Folder', os.getcwd())[0]

class Storage:
    def __init__(self, path, comment = ''):
        self.path = path
        self.File = h5py.File(self.path, 'a')
        self.addTime(self.File)
        self.addComment(self.File, comment)
          
    def addAttr(self, group, name, val):
        group.attrs[name] = val
    
    def addTime(self, group):
        self.addAttr(group, 'time', strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    
    def addComment(self, group, comment):
        self.addAttr(group, 'comment', comment)
    
    def addDataRaw(self, name, data = []):
        if name in self.File:
            del self.File[name]
        d = self.File.create_dataset(name, data = data)
        self.addTime(d)
    
    def addData(self, devName, paraName, val, cat = 'config', label = '', unit = '', comment = ''):
        name = cat+'/'+devName+'/'+paraName
        self.addDataRaw(name, val)
        self.addAttr(self.File[name], 'label', label)       
        self.addAttr(self.File[name], 'unit', unit)   
        self.addComment(self.File[name], comment)   
    
    def close(self):
        self.File.close()

class StorageRead:
    def __init__(self, path):
        self.path = path
        try:
            self.File = h5py.File(path, 'r')
        except:
            self.File = None
            print('Could not open file.')
    
    def getData(self, devName, paraName, cat = 'config'):
        if self.File != None:
            name = cat+'/'+devName+'/'+paraName
            if name in self.File:
                return self.File[name].value
            else: 
                print(name, ' not found.')
                return None
    
    def close(self):
       self.File.close()     
       
       
       
#s = StorageRead(r'C:\Users\hermann_b\Desktop\test\test.hdf5')