# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './manual.ui',
# licensing of './manual.ui' applies.
#
# Created: Mon Feb 11 20:51:02 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(492, 464)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(400, 430, 81, 22))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(340, 10, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.versionLabel = QtWidgets.QLabel(Dialog)
        self.versionLabel.setGeometry(QtCore.QRect(430, 30, 51, 16))
        self.versionLabel.setObjectName("versionLabel")
        self.textBrowser_2 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_2.setGeometry(QtCore.QRect(10, 70, 471, 351))
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(10, 50, 301, 16))
        self.label_6.setObjectName("label_6")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("Dialog", "Close", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "pyFileSearcher", None, -1))
        self.versionLabel.setText(QtWidgets.QApplication.translate("Dialog", "(v. 0.9)", None, -1))
        self.textBrowser_2.setHtml(QtWidgets.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">pyFileSearcher was designed as a lightweight, easy to use, portable tool powerful enough to get rid against enterprise level fileserver and give an answer for question: where is the space?</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This application can create index for your files, save it to database (sqlite for portability,  mysql maybe later) and then find files fast byrobust properties like part of filename or path, extension, size and date of indexing for a first time, so you can always to see which files were added by someone in the last days. Also you can save search options as templates for quick access.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">You can create index for all files, or use white or black lists for</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">extensions. And of course you can run indexing through gui, but also after setup parameters you can use special command line key for starting indexing via scheduler.</p></body></html>", None, -1))
        self.label_6.setText(QtWidgets.QApplication.translate("Dialog", "Short manual", None, -1))

