# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './preferences.ui',
# licensing of './preferences.ui' applies.
#
# Created: Fri Feb  8 19:12:14 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(390, 166)
        self.preferences = QtWidgets.QDialogButtonBox(Dialog)
        self.preferences.setGeometry(QtCore.QRect(20, 120, 341, 32))
        self.preferences.setOrientation(QtCore.Qt.Horizontal)
        self.preferences.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.preferences.setObjectName("preferences")
        self.PREFUseExternalDB = QtWidgets.QCheckBox(Dialog)
        self.PREFUseExternalDB.setGeometry(QtCore.QRect(20, 20, 131, 20))
        self.PREFUseExternalDB.setObjectName("PREFUseExternalDB")
        self.PREFDisableWindowsLongPathSupport = QtWidgets.QCheckBox(Dialog)
        self.PREFDisableWindowsLongPathSupport.setGeometry(QtCore.QRect(20, 50, 251, 20))
        self.PREFDisableWindowsLongPathSupport.setObjectName("PREFDisableWindowsLongPathSupport")
        self.PREFMaxSearchResults = QtWidgets.QSpinBox(Dialog)
        self.PREFMaxSearchResults.setGeometry(QtCore.QRect(250, 80, 121, 20))
        self.PREFMaxSearchResults.setMinimum(10)
        self.PREFMaxSearchResults.setMaximum(999999999)
        self.PREFMaxSearchResults.setObjectName("PREFMaxSearchResults")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 80, 231, 20))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.preferences, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.preferences, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.PREFUseExternalDB.setText(QtWidgets.QApplication.translate("Dialog", "Use external DB", None, -1))
        self.PREFDisableWindowsLongPathSupport.setText(QtWidgets.QApplication.translate("Dialog", "Disable Windows long path support", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Maximum search results by default: ", None, -1))

