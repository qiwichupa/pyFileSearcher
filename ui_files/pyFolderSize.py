# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'folderSize.ui',
# licensing of 'folderSize.ui' applies.
#
# Created: Wed Mar 20 08:47:42 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(457, 90)
        self.linePath = QtWidgets.QLineEdit(Dialog)
        self.linePath.setGeometry(QtCore.QRect(10, 20, 331, 22))
        self.linePath.setObjectName("linePath")
        self.browseButton = QtWidgets.QPushButton(Dialog)
        self.browseButton.setGeometry(QtCore.QRect(360, 20, 81, 22))
        self.browseButton.setObjectName("browseButton")
        self.buttonGetSize = QtWidgets.QPushButton(Dialog)
        self.buttonGetSize.setGeometry(QtCore.QRect(10, 50, 431, 22))
        self.buttonGetSize.setObjectName("buttonGetSize")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.browseButton.setText(QtWidgets.QApplication.translate("Dialog", "Browse...", None, -1))
        self.buttonGetSize.setText(QtWidgets.QApplication.translate("Dialog", "Get Size", None, -1))

