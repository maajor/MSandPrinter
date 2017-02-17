# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 17:03:12 2017

@author: Maajor
"""
#first compile ui in cmd: pyuic5 gcodesenderui.ui -o GCodeSenderUI.py

import os
os.chdir("D:\\GraduateYear2\\Thesis\\3 Machine\\MSandPrinter\\Marlin\\GCodeSender")

import serial
from serial.tools import list_ports

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from GCodeSenderUI import Ui_GCodeSenderUI

class SerialCon(QtCore.QThread):

    received = QtCore.pyqtSignal(object)
    okreceived = QtCore.pyqtSignal(object)
    myser = serial.Serial()

    def __init__(self, ser, parent=None):
        QtCore.QThread.__init__(self)
        # specify thread context for signals and slots:
        # test: comment following line, and run again
        self.moveToThread(self)
        # timer:
        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.readData)
        self.myser = ser

    def run(self):
        self.timer.start()
        #start eventloop
        self.exec_()

    def readData(self):
        # keeping the thread busy
        # figure out if the GUI remains responsive (should be running on a different thread)
        result = self.myser.readline()
        if result[0:-2] == "ok":
            self.okreceived.emit("yes")
        
        self.received.emit(result[0:-2])# line end with \r\n, remove last \n
       

class GCodeSenderApp(QMainWindow, Ui_GCodeSenderUI):
    ser = 0 # serial port
    get_okay = 0
    inSendingFile = False
    
    def __init__(self, parent=None):
        super(GCodeSenderApp, self).__init__(parent)
        self.setupUi(self)
        
        self.findComs()
        self.connectButton.clicked.connect(self.comConnect)
        self.sendLineButton.clicked.connect(self.sendLine)
        self.lineEdit.returnPressed.connect(self.sendLine)
        self.selectFileButton.clicked.connect(self.getFilePath)
        self.sendgcodeButton.clicked.connect(self.sendFile)
        
    def displayText(self, text):
        self.textBrowser.append(text)
        
    def comConnect(self):
        try:
            self.ser = serial.Serial(self.portSelect.currentText(), int(self.bdrateSelect.currentText()))
            self.displayText(self.portSelect.currentText() + " connected successfully")
            self.usingMoveToThread()
        except Exception as e:
            self.displayText(self.portSelect.currentText() + " open failed")
            self.displayText( str(e))
        
    def findComs(self):
        #find all available ports
        for ports in list_ports.comports():
            for port in ports:
                if port[0:3] == "COM":
                    self.portSelect.addItem(port)
        self.bdrateSelect.addItem("9600")
        self.bdrateSelect.addItem("115200")
        self.bdrateSelect.addItem("250000")
    
    def sendLine(self):
        sendtext = self.lineEdit.text()

        if (self.ser == 0) or ( self.ser.isOpen() == False ) :
            self.displayText("Port not ready, please connect it")
            return
        elif sendtext == "":
            self.displayText("No Command Send")
            return
        else:
            sendtext = str( sendtext + "\n")
            try:
                self.ser.write(sendtext)
            except Exception as e:
                self.displayText("send command fail")
                self.displayText( str(e))
    
    def getFilePath(self):
        fileName = QFileDialog.getOpenFileName(self, filter = "GCode (*.gcode *.txt)")
        self.filePath.setText(fileName[0])
        
    def sendFile(self):
        #error handling: port not open or no file.
        if (self.ser == 0) or ( self.ser.isOpen() == False ) :
            self.displayText("Port not ready, please connect it")
            return
        self.filename = self.filePath.text() 
        if self.filename == "":
            self.displayText("Please select a file")
            return
        
        #try open file
        try:
            self.gcodeFile = open(self.filename, "r")
        except Exception as e:
            self.displayText("File open failed")
            self.displayText( str(e))
        
        #total lines count
        self.num_lines = sum(1 for line in open(self.filename, "r"))
        #when file has less than 2 lines
        if self.num_lines < 2:
            current_line = self.gcodeFile.readline()
            self.ser.write(current_line)
        #when file has more than 2 lines
        else:
            #current line is the command on move
            #next line is the command that has been sent but in buffer
            self.current_linenum = 0
            self.current_line = self.gcodeFile.readline()
            self.next_line = self.gcodeFile.readline()
            #self.displayText(">>>Sending " + self.current_line)
            self.ser.write(self.current_line)
            #self.displayText(">>>Sending " + self.next_line)
            self.ser.write(self.next_line)
            self.lineCurrent.setText("Current At Line " + str(self.current_linenum) + ":" + self.current_line)
            self.current_linenum = 1
            self.inSendingFile = True
    
    def findOk(self, text):
        if self.inSendingFile and self.current_linenum < self.num_lines :
            #get new line and send lastest line
            self.current_line = self.next_line
            self.next_line = self.gcodeFile.readline()
            #self.displayText(">>>Sending " + self.next_line)
            self.ser.write(self.next_line)
            
            #display current line and progress
            self.lineCurrent.setText("Current At Line " + str(self.current_linenum) + ":" + self.current_line)
            self.progressBar.setValue( (self.current_linenum + 1) * 100 /  self.num_lines)
            
            self.current_linenum = self.current_linenum + 1
        if self.current_linenum == self.num_lines :
            self.lineCurrent.setText("Print Job finished at " + self.filename)
            self.inSendingFile = False
    
            
    def closeEvent(self, event):
        if self.ser != 0:
            self.ser.close()
        self.serialc.quit();

    def usingMoveToThread(self):
        self.serialc = SerialCon(self.ser)
        # binding signals:
        self.serialc.received.connect(self.displayText)
        self.serialc.okreceived.connect(self.findOk)
        # start thread
        self.serialc.start()

def main():
    app = QApplication(sys.argv)
    form = GCodeSenderApp()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    main()