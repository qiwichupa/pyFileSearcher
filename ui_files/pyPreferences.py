# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui',
# licensing of 'preferences.ui' applies.
#
# Created: Fri Mar 29 11:32:26 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(390, 270)
        Dialog.setMinimumSize(QtCore.QSize(390, 270))
        Dialog.setMaximumSize(QtCore.QSize(390, 270))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/prefs.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.preferences = QtWidgets.QDialogButtonBox(Dialog)
        self.preferences.setGeometry(QtCore.QRect(27, 240, 341, 20))
        self.preferences.setOrientation(QtCore.Qt.Horizontal)
        self.preferences.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.preferences.setObjectName("preferences")
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(5, 9, 381, 229))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setObjectName("gridLayout")
        self.PREFUseExternalDB = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.PREFUseExternalDB.setObjectName("PREFUseExternalDB")
        self.gridLayout.addWidget(self.PREFUseExternalDB, 0, 0, 1, 1)
        self.PREFMaxSearchResults = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.PREFMaxSearchResults.setMinimum(10)
        self.PREFMaxSearchResults.setMaximum(999999999)
        self.PREFMaxSearchResults.setObjectName("PREFMaxSearchResults")
        self.gridLayout.addWidget(self.PREFMaxSearchResults, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 7, 0, 1, 1)
        self.PREFsqlTransactionLimit = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.PREFsqlTransactionLimit.setMinimum(1)
        self.PREFsqlTransactionLimit.setMaximum(999999999)
        self.PREFsqlTransactionLimit.setProperty("value", 1)
        self.PREFsqlTransactionLimit.setObjectName("PREFsqlTransactionLimit")
        self.gridLayout.addWidget(self.PREFsqlTransactionLimit, 7, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.PREFDisableWindowsLongPathSupport = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.PREFDisableWindowsLongPathSupport.setObjectName("PREFDisableWindowsLongPathSupport")
        self.gridLayout.addWidget(self.PREFDisableWindowsLongPathSupport, 6, 0, 1, 1)
        self.PREFSaveRemovedInfoDays = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.PREFSaveRemovedInfoDays.setMinimum(0)
        self.PREFSaveRemovedInfoDays.setMaximum(999999999)
        self.PREFSaveRemovedInfoDays.setProperty("value", 0)
        self.PREFSaveRemovedInfoDays.setObjectName("PREFSaveRemovedInfoDays")
        self.gridLayout.addWidget(self.PREFSaveRemovedInfoDays, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.PREFLoggingLevel = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.PREFLoggingLevel.setObjectName("PREFLoggingLevel")
        self.PREFLoggingLevel.addItem("")
        self.PREFLoggingLevel.addItem("")
        self.PREFLoggingLevel.addItem("")
        self.gridLayout.addWidget(self.PREFLoggingLevel, 3, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.gridLayoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 4, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.preferences, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.preferences, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.PREFUseExternalDB.setText(QtWidgets.QApplication.translate("Dialog", "Use MySQL", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("Dialog", "Save removed files info for a days", None, -1))
        self.label_5.setText(QtWidgets.QApplication.translate("Dialog", "<html><head/><body><p><span style=\" color:#000000;\">MySQL update limit (files per transaction):</span></p></body></html>", None, -1))
        self.label_6.setText(QtWidgets.QApplication.translate("Dialog", "<html><head/><body><p>These settings should remain default in most cases.</p></body></html>", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Maximum search results by default: ", None, -1))
        self.PREFDisableWindowsLongPathSupport.setText(QtWidgets.QApplication.translate("Dialog", "Disable Windows long path support", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Logging level:", None, -1))
        self.PREFLoggingLevel.setItemText(0, QtWidgets.QApplication.translate("Dialog", "DEBUG", None, -1))
        self.PREFLoggingLevel.setItemText(1, QtWidgets.QApplication.translate("Dialog", "INFO", None, -1))
        self.PREFLoggingLevel.setItemText(2, QtWidgets.QApplication.translate("Dialog", "WARNING", None, -1))

import icons_rc
