# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui',
# licensing of 'preferences.ui' applies.
#
# Created: Mon Mar 18 12:01:30 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(390, 200)
        Dialog.setMinimumSize(QtCore.QSize(390, 200))
        Dialog.setMaximumSize(QtCore.QSize(390, 200))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/prefs.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.preferences = QtWidgets.QDialogButtonBox(Dialog)
        self.preferences.setGeometry(QtCore.QRect(27, 170, 341, 20))
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
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 140, 91, 20))
        self.label_2.setObjectName("label_2")
        self.PREFLoggingLevel = QtWidgets.QComboBox(Dialog)
        self.PREFLoggingLevel.setGeometry(QtCore.QRect(120, 140, 81, 20))
        self.PREFLoggingLevel.setObjectName("PREFLoggingLevel")
        self.PREFLoggingLevel.addItem("")
        self.PREFLoggingLevel.addItem("")
        self.PREFLoggingLevel.addItem("")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 110, 151, 20))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(236, 110, 40, 20))
        self.label_4.setObjectName("label_4")
        self.PREFSaveRemovedInfoDays = QtWidgets.QSpinBox(Dialog)
        self.PREFSaveRemovedInfoDays.setGeometry(QtCore.QRect(170, 110, 61, 20))
        self.PREFSaveRemovedInfoDays.setMinimum(0)
        self.PREFSaveRemovedInfoDays.setMaximum(999999999)
        self.PREFSaveRemovedInfoDays.setProperty("value", 0)
        self.PREFSaveRemovedInfoDays.setObjectName("PREFSaveRemovedInfoDays")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.preferences, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.preferences, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.PREFUseExternalDB.setText(QtWidgets.QApplication.translate("Dialog", "Use external DB", None, -1))
        self.PREFDisableWindowsLongPathSupport.setText(QtWidgets.QApplication.translate("Dialog", "Disable Windows long path support", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Maximum search results by default: ", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Logging level:", None, -1))
        self.PREFLoggingLevel.setItemText(0, QtWidgets.QApplication.translate("Dialog", "DEBUG", None, -1))
        self.PREFLoggingLevel.setItemText(1, QtWidgets.QApplication.translate("Dialog", "INFO", None, -1))
        self.PREFLoggingLevel.setItemText(2, QtWidgets.QApplication.translate("Dialog", "WARNING", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("Dialog", "Save removed files info", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("Dialog", "day(s)", None, -1))

import icons_rc
