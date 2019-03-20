# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'folderSize.ui',
# licensing of 'folderSize.ui' applies.
#
# Created: Wed Mar 20 14:57:05 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(451, 149)
        Dialog.setMinimumSize(QtCore.QSize(451, 149))
        Dialog.setMaximumSize(QtCore.QSize(451, 149))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/main.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.linePath = QtWidgets.QLineEdit(Dialog)
        self.linePath.setGeometry(QtCore.QRect(10, 90, 331, 22))
        self.linePath.setObjectName("linePath")
        self.browseButton = QtWidgets.QPushButton(Dialog)
        self.browseButton.setGeometry(QtCore.QRect(360, 90, 81, 22))
        self.browseButton.setObjectName("browseButton")
        self.buttonGetSize = QtWidgets.QPushButton(Dialog)
        self.buttonGetSize.setGeometry(QtCore.QRect(10, 120, 431, 22))
        self.buttonGetSize.setObjectName("buttonGetSize")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 431, 71))
        self.label.setMaximumSize(QtCore.QSize(431, 16777215))
        self.label.setWordWrap(True)
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.browseButton.setText(QtWidgets.QApplication.translate("Dialog", "Browse...", None, -1))
        self.buttonGetSize.setText(QtWidgets.QApplication.translate("Dialog", "Get Size", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "<html><head/><body><p><span style=\" color:#000000;\">Make sure that the entire directory, the size of which you want to find out, has been indexed.</span></p><p><span style=\" color:#ff0000;\">If only the D:\\app\\ and D:\\work\\ directories were indexed, the D:\\ size query will return only their total size.</span></p></body></html>", None, -1))

import icons_rc
