# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui',
# licensing of 'main.ui' applies.
#
# Created: Mon Mar 18 12:01:21 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1006, 660)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/main.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.layoutBottom = QtWidgets.QGridLayout()
        self.layoutBottom.setSpacing(0)
        self.layoutBottom.setObjectName("layoutBottom")
        self.tableFiles = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableFiles.sizePolicy().hasHeightForWidth())
        self.tableFiles.setSizePolicy(sizePolicy)
        self.tableFiles.setMinimumSize(QtCore.QSize(0, 200))
        self.tableFiles.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tableFiles.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableFiles.setAutoScroll(False)
        self.tableFiles.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.tableFiles.setTabKeyNavigation(False)
        self.tableFiles.setProperty("showDropIndicator", True)
        self.tableFiles.setDragDropOverwriteMode(True)
        self.tableFiles.setAlternatingRowColors(True)
        self.tableFiles.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tableFiles.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableFiles.setTextElideMode(QtCore.Qt.ElideRight)
        self.tableFiles.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableFiles.setShowGrid(True)
        self.tableFiles.setGridStyle(QtCore.Qt.SolidLine)
        self.tableFiles.setWordWrap(False)
        self.tableFiles.setCornerButtonEnabled(True)
        self.tableFiles.setObjectName("tableFiles")
        self.tableFiles.setColumnCount(8)
        self.tableFiles.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(7, item)
        self.tableFiles.horizontalHeader().setStretchLastSection(True)
        self.tableFiles.verticalHeader().setVisible(False)
        self.tableFiles.verticalHeader().setDefaultSectionSize(20)
        self.tableFiles.verticalHeader().setMinimumSectionSize(20)
        self.layoutBottom.addWidget(self.tableFiles, 1, 0, 1, 1)
        self.tabsSearch = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabsSearch.sizePolicy().hasHeightForWidth())
        self.tabsSearch.setSizePolicy(sizePolicy)
        self.tabsSearch.setMaximumSize(QtCore.QSize(16777215, 200))
        self.tabsSearch.setObjectName("tabsSearch")
        self.tabMain = QtWidgets.QWidget()
        self.tabMain.setObjectName("tabMain")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tabMain)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(self.tabMain)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelFilters = QtWidgets.QLabel(self.frame)
        self.labelFilters.setMaximumSize(QtCore.QSize(50, 16777215))
        self.labelFilters.setObjectName("labelFilters")
        self.gridLayout_2.addWidget(self.labelFilters, 0, 0, 1, 1)
        self.btnSearch = QtWidgets.QPushButton(self.frame)
        self.btnSearch.setObjectName("btnSearch")
        self.gridLayout_2.addWidget(self.btnSearch, 4, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 5, 0, 1, 1)
        self.FilterFilename = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FilterFilename.sizePolicy().hasHeightForWidth())
        self.FilterFilename.setSizePolicy(sizePolicy)
        self.FilterFilename.setText("")
        self.FilterFilename.setObjectName("FilterFilename")
        self.gridLayout_2.addWidget(self.FilterFilename, 1, 0, 1, 4)
        self.FilterPath = QtWidgets.QLineEdit(self.frame)
        self.FilterPath.setText("")
        self.FilterPath.setObjectName("FilterPath")
        self.gridLayout_2.addWidget(self.FilterPath, 2, 0, 1, 4)
        self.FilterFileTypes = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FilterFileTypes.sizePolicy().hasHeightForWidth())
        self.FilterFileTypes.setSizePolicy(sizePolicy)
        self.FilterFileTypes.setText("")
        self.FilterFileTypes.setObjectName("FilterFileTypes")
        self.gridLayout_2.addWidget(self.FilterFileTypes, 3, 0, 1, 4)
        self.FilterSearchInRemoved = QtWidgets.QCheckBox(self.frame)
        self.FilterSearchInRemoved.setMaximumSize(QtCore.QSize(140, 16777215))
        self.FilterSearchInRemoved.setObjectName("FilterSearchInRemoved")
        self.gridLayout_2.addWidget(self.FilterSearchInRemoved, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 1, 1, 2)
        self.FilterShowMoreResultsCheckbox = QtWidgets.QCheckBox(self.frame)
        self.FilterShowMoreResultsCheckbox.setObjectName("FilterShowMoreResultsCheckbox")
        self.gridLayout_2.addWidget(self.FilterShowMoreResultsCheckbox, 4, 1, 1, 3)
        self.horizontalLayout.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.tabMain)
        self.frame_2.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(250, 0))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.FilterMinSize = QtWidgets.QSpinBox(self.frame_2)
        self.FilterMinSize.setEnabled(False)
        self.FilterMinSize.setGeometry(QtCore.QRect(90, 30, 91, 21))
        self.FilterMinSize.setMaximum(999999999)
        self.FilterMinSize.setObjectName("FilterMinSize")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 151, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(50)
        font.setBold(False)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.FilterMaxSize = QtWidgets.QSpinBox(self.frame_2)
        self.FilterMaxSize.setEnabled(False)
        self.FilterMaxSize.setGeometry(QtCore.QRect(90, 50, 91, 21))
        self.FilterMaxSize.setMaximum(999999999)
        self.FilterMaxSize.setObjectName("FilterMaxSize")
        self.FilterMinSizeEnabled = QtWidgets.QCheckBox(self.frame_2)
        self.FilterMinSizeEnabled.setGeometry(QtCore.QRect(10, 30, 85, 20))
        self.FilterMinSizeEnabled.setObjectName("FilterMinSizeEnabled")
        self.FilterMaxSizeEnabled = QtWidgets.QCheckBox(self.frame_2)
        self.FilterMaxSizeEnabled.setGeometry(QtCore.QRect(10, 50, 85, 20))
        self.FilterMaxSizeEnabled.setObjectName("FilterMaxSizeEnabled")
        self.FilterMinSizeType = QtWidgets.QComboBox(self.frame_2)
        self.FilterMinSizeType.setEnabled(False)
        self.FilterMinSizeType.setGeometry(QtCore.QRect(190, 30, 51, 22))
        self.FilterMinSizeType.setObjectName("FilterMinSizeType")
        self.FilterMinSizeType.addItem("")
        self.FilterMinSizeType.addItem("")
        self.FilterMinSizeType.addItem("")
        self.FilterMinSizeType.addItem("")
        self.FilterMaxSizeType = QtWidgets.QComboBox(self.frame_2)
        self.FilterMaxSizeType.setEnabled(False)
        self.FilterMaxSizeType.setGeometry(QtCore.QRect(190, 50, 51, 22))
        self.FilterMaxSizeType.setObjectName("FilterMaxSizeType")
        self.FilterMaxSizeType.addItem("")
        self.FilterMaxSizeType.addItem("")
        self.FilterMaxSizeType.addItem("")
        self.FilterMaxSizeType.addItem("")
        self.FilterIndexedLastDaysEnabled = QtWidgets.QCheckBox(self.frame_2)
        self.FilterIndexedLastDaysEnabled.setGeometry(QtCore.QRect(10, 77, 121, 20))
        self.FilterIndexedLastDaysEnabled.setObjectName("FilterIndexedLastDaysEnabled")
        self.FilterIndexedLastDays = QtWidgets.QSpinBox(self.frame_2)
        self.FilterIndexedLastDays.setEnabled(False)
        self.FilterIndexedLastDays.setGeometry(QtCore.QRect(125, 76, 56, 21))
        self.FilterIndexedLastDays.setMinimum(1)
        self.FilterIndexedLastDays.setMaximum(999)
        self.FilterIndexedLastDays.setObjectName("FilterIndexedLastDays")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(190, 77, 41, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(10, 106, 91, 14))
        self.label_2.setObjectName("label_2")
        self.FilterListRemoveButton = QtWidgets.QPushButton(self.frame_2)
        self.FilterListRemoveButton.setGeometry(QtCore.QRect(110, 126, 15, 20))
        self.FilterListRemoveButton.setObjectName("FilterListRemoveButton")
        self.FilterListSaveButton = QtWidgets.QPushButton(self.frame_2)
        self.FilterListSaveButton.setGeometry(QtCore.QRect(230, 126, 15, 20))
        self.FilterListSaveButton.setObjectName("FilterListSaveButton")
        self.FilterListComboBox = QtWidgets.QComboBox(self.frame_2)
        self.FilterListComboBox.setGeometry(QtCore.QRect(10, 126, 100, 20))
        self.FilterListComboBox.setObjectName("FilterListComboBox")
        self.FilterListComboBox.addItem("")
        self.FilterListComboBox.setItemText(0, "")
        self.FilterListLineEdit = QtWidgets.QLineEdit(self.frame_2)
        self.FilterListLineEdit.setGeometry(QtCore.QRect(130, 126, 100, 20))
        self.FilterListLineEdit.setObjectName("FilterListLineEdit")
        self.horizontalLayout.addWidget(self.frame_2)
        self.tabsSearch.addTab(self.tabMain, "")
        self.tabDatabaseSettings = QtWidgets.QWidget()
        self.tabDatabaseSettings.setEnabled(True)
        self.tabDatabaseSettings.setObjectName("tabDatabaseSettings")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tabDatabaseSettings)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_3 = QtWidgets.QFrame(self.tabDatabaseSettings)
        self.frame_3.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.DBRootScanPathLabel = QtWidgets.QLabel(self.frame_3)
        self.DBRootScanPathLabel.setObjectName("DBRootScanPathLabel")
        self.gridLayout.addWidget(self.DBRootScanPathLabel, 3, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.frame_3)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 1, 1, 1, 1)
        self.DBSettingsLabel = QtWidgets.QLabel(self.frame_3)
        self.DBSettingsLabel.setObjectName("DBSettingsLabel")
        self.gridLayout.addWidget(self.DBSettingsLabel, 2, 0, 1, 7)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 5, 6, 1, 1)
        self.DBCountLabel = QtWidgets.QLabel(self.frame_3)
        self.DBCountLabel.setObjectName("DBCountLabel")
        self.gridLayout.addWidget(self.DBCountLabel, 0, 5, 1, 1)
        self.DBCount = QtWidgets.QSpinBox(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DBCount.sizePolicy().hasHeightForWidth())
        self.DBCount.setSizePolicy(sizePolicy)
        self.DBCount.setInputMethodHints(QtCore.Qt.ImhNone)
        self.DBCount.setFrame(True)
        self.DBCount.setReadOnly(False)
        self.DBCount.setAccelerated(False)
        self.DBCount.setMinimum(1)
        self.DBCount.setMaximum(9)
        self.DBCount.setObjectName("DBCount")
        self.gridLayout.addWidget(self.DBCount, 0, 6, 1, 1)
        self.DBSelectDatabase = QtWidgets.QComboBox(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DBSelectDatabase.sizePolicy().hasHeightForWidth())
        self.DBSelectDatabase.setSizePolicy(sizePolicy)
        self.DBSelectDatabase.setMinimumSize(QtCore.QSize(60, 0))
        self.DBSelectDatabase.setMaximumSize(QtCore.QSize(60, 16777215))
        self.DBSelectDatabase.setObjectName("DBSelectDatabase")
        self.gridLayout.addWidget(self.DBSelectDatabase, 0, 1, 1, 1)
        self.DBSelectDatabaseLabel = QtWidgets.QLabel(self.frame_3)
        self.DBSelectDatabaseLabel.setObjectName("DBSelectDatabaseLabel")
        self.gridLayout.addWidget(self.DBSelectDatabaseLabel, 0, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 2, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.frame_3)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 2, 1, 1)
        self.DBFileTypeFilter = QtWidgets.QLineEdit(self.frame_3)
        self.DBFileTypeFilter.setObjectName("DBFileTypeFilter")
        self.gridLayout.addWidget(self.DBFileTypeFilter, 4, 1, 1, 2)
        self.DBRootScanPath = QtWidgets.QComboBox(self.frame_3)
        self.DBRootScanPath.setCurrentText("")
        self.DBRootScanPath.setObjectName("DBRootScanPath")
        self.DBRootScanPath.addItem("")
        self.DBRootScanPath.setItemText(0, "")
        self.DBRootScanPath.addItem("")
        self.gridLayout.addWidget(self.DBRootScanPath, 3, 1, 1, 1)
        self.line = QtWidgets.QFrame(self.frame_3)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 5, 1, 1)
        self.line_4 = QtWidgets.QFrame(self.frame_3)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout.addWidget(self.line_4, 1, 6, 1, 1)
        self.line_6 = QtWidgets.QFrame(self.frame_3)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.gridLayout.addWidget(self.line_6, 1, 4, 1, 1)
        self.DBFileTypeFilterLabel = QtWidgets.QLabel(self.frame_3)
        self.DBFileTypeFilterLabel.setObjectName("DBFileTypeFilterLabel")
        self.gridLayout.addWidget(self.DBFileTypeFilterLabel, 4, 0, 1, 1)
        self.line_7 = QtWidgets.QFrame(self.frame_3)
        self.line_7.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.gridLayout.addWidget(self.line_7, 1, 0, 1, 1)
        self.line_5 = QtWidgets.QFrame(self.frame_3)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout.addWidget(self.line_5, 1, 3, 1, 1)
        self.DBFileTypeFilterMode = QtWidgets.QComboBox(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DBFileTypeFilterMode.sizePolicy().hasHeightForWidth())
        self.DBFileTypeFilterMode.setSizePolicy(sizePolicy)
        self.DBFileTypeFilterMode.setMinimumSize(QtCore.QSize(80, 0))
        self.DBFileTypeFilterMode.setObjectName("DBFileTypeFilterMode")
        self.DBFileTypeFilterMode.addItem("")
        self.DBFileTypeFilterMode.addItem("")
        self.gridLayout.addWidget(self.DBFileTypeFilterMode, 4, 5, 1, 2)
        self.DBApplySettingsButton = QtWidgets.QPushButton(self.frame_3)
        self.DBApplySettingsButton.setObjectName("DBApplySettingsButton")
        self.gridLayout.addWidget(self.DBApplySettingsButton, 5, 1, 1, 1)
        self.horizontalLayout_4.addWidget(self.frame_3)
        self.tabsSearch.addTab(self.tabDatabaseSettings, "")
        self.tabMySQL = QtWidgets.QWidget()
        self.tabMySQL.setObjectName("tabMySQL")
        self.MySQLServerAddress = QtWidgets.QLineEdit(self.tabMySQL)
        self.MySQLServerAddress.setGeometry(QtCore.QRect(10, 20, 141, 22))
        self.MySQLServerAddress.setText("")
        self.MySQLServerAddress.setObjectName("MySQLServerAddress")
        self.MySQLDBName = QtWidgets.QLineEdit(self.tabMySQL)
        self.MySQLDBName.setGeometry(QtCore.QRect(10, 50, 190, 22))
        self.MySQLDBName.setObjectName("MySQLDBName")
        self.MySQLLogin = QtWidgets.QLineEdit(self.tabMySQL)
        self.MySQLLogin.setGeometry(QtCore.QRect(10, 80, 190, 22))
        self.MySQLLogin.setObjectName("MySQLLogin")
        self.MySQLPassword = QtWidgets.QLineEdit(self.tabMySQL)
        self.MySQLPassword.setGeometry(QtCore.QRect(10, 110, 190, 22))
        self.MySQLPassword.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.MySQLPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.MySQLPassword.setClearButtonEnabled(False)
        self.MySQLPassword.setObjectName("MySQLPassword")
        self.MySQLTestButton = QtWidgets.QPushButton(self.tabMySQL)
        self.MySQLTestButton.setGeometry(QtCore.QRect(220, 60, 131, 31))
        self.MySQLTestButton.setObjectName("MySQLTestButton")
        self.MySQLServerPort = QtWidgets.QLineEdit(self.tabMySQL)
        self.MySQLServerPort.setGeometry(QtCore.QRect(159, 20, 40, 22))
        self.MySQLServerPort.setText("")
        self.MySQLServerPort.setObjectName("MySQLServerPort")
        self.label_4 = QtWidgets.QLabel(self.tabMySQL)
        self.label_4.setGeometry(QtCore.QRect(154, 22, 16, 16))
        self.label_4.setObjectName("label_4")
        self.MySQLInitDBButton = QtWidgets.QPushButton(self.tabMySQL)
        self.MySQLInitDBButton.setEnabled(False)
        self.MySQLInitDBButton.setGeometry(QtCore.QRect(270, 100, 81, 22))
        self.MySQLInitDBButton.setObjectName("MySQLInitDBButton")
        self.MySQLInitDBCheckBox = QtWidgets.QCheckBox(self.tabMySQL)
        self.MySQLInitDBCheckBox.setEnabled(False)
        self.MySQLInitDBCheckBox.setGeometry(QtCore.QRect(249, 101, 16, 20))
        self.MySQLInitDBCheckBox.setText("")
        self.MySQLInitDBCheckBox.setObjectName("MySQLInitDBCheckBox")
        self.MySQLPathsTable = QtWidgets.QTableWidget(self.tabMySQL)
        self.MySQLPathsTable.setGeometry(QtCore.QRect(370, 10, 491, 151))
        self.MySQLPathsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.MySQLPathsTable.setAlternatingRowColors(True)
        self.MySQLPathsTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.MySQLPathsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.MySQLPathsTable.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.MySQLPathsTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.MySQLPathsTable.setWordWrap(False)
        self.MySQLPathsTable.setCornerButtonEnabled(False)
        self.MySQLPathsTable.setObjectName("MySQLPathsTable")
        self.MySQLPathsTable.setColumnCount(1)
        self.MySQLPathsTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.MySQLPathsTable.setHorizontalHeaderItem(0, item)
        self.MySQLPathsTable.horizontalHeader().setStretchLastSection(True)
        self.MySQLPathsTable.verticalHeader().setVisible(False)
        self.MySQLPathsTable.verticalHeader().setDefaultSectionSize(20)
        self.MySQLPathsTable.verticalHeader().setMinimumSectionSize(20)
        self.MySQLPathsTableAddButton = QtWidgets.QPushButton(self.tabMySQL)
        self.MySQLPathsTableAddButton.setGeometry(QtCore.QRect(870, 10, 81, 22))
        self.MySQLPathsTableAddButton.setObjectName("MySQLPathsTableAddButton")
        self.MySQLPathsTableRemoveButton = QtWidgets.QPushButton(self.tabMySQL)
        self.MySQLPathsTableRemoveButton.setGeometry(QtCore.QRect(870, 40, 81, 22))
        self.MySQLPathsTableRemoveButton.setObjectName("MySQLPathsTableRemoveButton")
        self.tabsSearch.addTab(self.tabMySQL, "")
        self.layoutBottom.addWidget(self.tabsSearch, 0, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.layoutBottom)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1006, 19))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.actionStartScan = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/scan.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStartScan.setIcon(icon1)
        self.actionStartScan.setObjectName("actionStartScan")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/prefs.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPreferences.setIcon(icon2)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionShowHelpInfo = QtWidgets.QAction(MainWindow)
        self.actionShowHelpInfo.setObjectName("actionShowHelpInfo")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionShowLog = QtWidgets.QAction(MainWindow)
        self.actionShowLog.setObjectName("actionShowLog")
        self.actionOpenWorkingDirectory = QtWidgets.QAction(MainWindow)
        self.actionOpenWorkingDirectory.setObjectName("actionOpenWorkingDirectory")
        self.menuFile.addAction(self.actionStartScan)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionShowLog)
        self.menuHelp.addAction(self.actionOpenWorkingDirectory)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionShowHelpInfo)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabsSearch.setCurrentIndex(0)
        QtCore.QObject.connect(self.FilterMinSizeEnabled, QtCore.SIGNAL("toggled(bool)"), self.FilterMinSize.setEnabled)
        QtCore.QObject.connect(self.FilterMaxSizeEnabled, QtCore.SIGNAL("toggled(bool)"), self.FilterMaxSize.setEnabled)
        QtCore.QObject.connect(self.FilterMinSizeEnabled, QtCore.SIGNAL("toggled(bool)"), self.FilterMinSizeType.setEnabled)
        QtCore.QObject.connect(self.FilterMaxSizeEnabled, QtCore.SIGNAL("toggled(bool)"), self.FilterMaxSizeType.setEnabled)
        QtCore.QObject.connect(self.FilterIndexedLastDaysEnabled, QtCore.SIGNAL("toggled(bool)"), self.FilterIndexedLastDays.setEnabled)
        QtCore.QObject.connect(self.MySQLInitDBCheckBox, QtCore.SIGNAL("stateChanged(int)"), self.MySQLInitDBButton.showNormal)
        QtCore.QObject.connect(self.FilterSearchInRemoved, QtCore.SIGNAL("toggled(bool)"), self.FilterIndexedLastDaysEnabled.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.FilterFilename, self.FilterPath)
        MainWindow.setTabOrder(self.FilterPath, self.FilterFileTypes)
        MainWindow.setTabOrder(self.FilterFileTypes, self.FilterMinSizeEnabled)
        MainWindow.setTabOrder(self.FilterMinSizeEnabled, self.FilterMinSize)
        MainWindow.setTabOrder(self.FilterMinSize, self.FilterMinSizeType)
        MainWindow.setTabOrder(self.FilterMinSizeType, self.FilterMaxSizeEnabled)
        MainWindow.setTabOrder(self.FilterMaxSizeEnabled, self.FilterMaxSize)
        MainWindow.setTabOrder(self.FilterMaxSize, self.FilterMaxSizeType)
        MainWindow.setTabOrder(self.FilterMaxSizeType, self.FilterIndexedLastDaysEnabled)
        MainWindow.setTabOrder(self.FilterIndexedLastDaysEnabled, self.FilterIndexedLastDays)
        MainWindow.setTabOrder(self.FilterIndexedLastDays, self.FilterListComboBox)
        MainWindow.setTabOrder(self.FilterListComboBox, self.FilterListRemoveButton)
        MainWindow.setTabOrder(self.FilterListRemoveButton, self.FilterListLineEdit)
        MainWindow.setTabOrder(self.FilterListLineEdit, self.FilterListSaveButton)
        MainWindow.setTabOrder(self.FilterListSaveButton, self.btnSearch)
        MainWindow.setTabOrder(self.btnSearch, self.tableFiles)
        MainWindow.setTabOrder(self.tableFiles, self.tabsSearch)
        MainWindow.setTabOrder(self.tabsSearch, self.DBSelectDatabase)
        MainWindow.setTabOrder(self.DBSelectDatabase, self.DBRootScanPath)
        MainWindow.setTabOrder(self.DBRootScanPath, self.DBFileTypeFilter)
        MainWindow.setTabOrder(self.DBFileTypeFilter, self.DBFileTypeFilterMode)
        MainWindow.setTabOrder(self.DBFileTypeFilterMode, self.DBApplySettingsButton)
        MainWindow.setTabOrder(self.DBApplySettingsButton, self.DBCount)
        MainWindow.setTabOrder(self.DBCount, self.MySQLServerAddress)
        MainWindow.setTabOrder(self.MySQLServerAddress, self.MySQLServerPort)
        MainWindow.setTabOrder(self.MySQLServerPort, self.MySQLDBName)
        MainWindow.setTabOrder(self.MySQLDBName, self.MySQLLogin)
        MainWindow.setTabOrder(self.MySQLLogin, self.MySQLPassword)
        MainWindow.setTabOrder(self.MySQLPassword, self.MySQLTestButton)
        MainWindow.setTabOrder(self.MySQLTestButton, self.MySQLInitDBCheckBox)
        MainWindow.setTabOrder(self.MySQLInitDBCheckBox, self.MySQLInitDBButton)
        MainWindow.setTabOrder(self.MySQLInitDBButton, self.MySQLPathsTableAddButton)
        MainWindow.setTabOrder(self.MySQLPathsTableAddButton, self.MySQLPathsTableRemoveButton)
        MainWindow.setTabOrder(self.MySQLPathsTableRemoveButton, self.MySQLPathsTable)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.tableFiles.setSortingEnabled(True)
        self.tableFiles.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "#", None, -1))
        self.tableFiles.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("MainWindow", "Filename", None, -1))
        self.tableFiles.horizontalHeaderItem(2).setText(QtWidgets.QApplication.translate("MainWindow", "Type", None, -1))
        self.tableFiles.horizontalHeaderItem(3).setText(QtWidgets.QApplication.translate("MainWindow", "Size", None, -1))
        self.tableFiles.horizontalHeaderItem(4).setText(QtWidgets.QApplication.translate("MainWindow", "Modified", None, -1))
        self.tableFiles.horizontalHeaderItem(5).setText(QtWidgets.QApplication.translate("MainWindow", "Indexed", None, -1))
        self.tableFiles.horizontalHeaderItem(6).setText(QtWidgets.QApplication.translate("MainWindow", "Created", None, -1))
        self.tableFiles.horizontalHeaderItem(7).setText(QtWidgets.QApplication.translate("MainWindow", "Path", None, -1))
        self.labelFilters.setText(QtWidgets.QApplication.translate("MainWindow", "Filters", None, -1))
        self.btnSearch.setText(QtWidgets.QApplication.translate("MainWindow", "Search...", None, -1))
        self.FilterFilename.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Filename filter", None, -1))
        self.FilterFilename.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Filename... (REQUIRED, wildcards supported)", None, -1))
        self.FilterPath.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Path contains... (wildcards supported)", None, -1))
        self.FilterFileTypes.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Filename filter", None, -1))
        self.FilterFileTypes.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Filetype (exe,txt,docx)", None, -1))
        self.FilterSearchInRemoved.setText(QtWidgets.QApplication.translate("MainWindow", "Search in removed", None, -1))
        self.FilterShowMoreResultsCheckbox.setText(QtWidgets.QApplication.translate("MainWindow", "Show More Results", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("MainWindow", "Additional filters", None, -1))
        self.FilterMinSizeEnabled.setText(QtWidgets.QApplication.translate("MainWindow", "Min size:", None, -1))
        self.FilterMaxSizeEnabled.setText(QtWidgets.QApplication.translate("MainWindow", "Max size:", None, -1))
        self.FilterMinSizeType.setItemText(0, QtWidgets.QApplication.translate("MainWindow", "b", None, -1))
        self.FilterMinSizeType.setItemText(1, QtWidgets.QApplication.translate("MainWindow", "Kb", None, -1))
        self.FilterMinSizeType.setItemText(2, QtWidgets.QApplication.translate("MainWindow", "Mb", None, -1))
        self.FilterMinSizeType.setItemText(3, QtWidgets.QApplication.translate("MainWindow", "Gb", None, -1))
        self.FilterMaxSizeType.setItemText(0, QtWidgets.QApplication.translate("MainWindow", "b", None, -1))
        self.FilterMaxSizeType.setItemText(1, QtWidgets.QApplication.translate("MainWindow", "Kb", None, -1))
        self.FilterMaxSizeType.setItemText(2, QtWidgets.QApplication.translate("MainWindow", "Mb", None, -1))
        self.FilterMaxSizeType.setItemText(3, QtWidgets.QApplication.translate("MainWindow", "Gb", None, -1))
        self.FilterIndexedLastDaysEnabled.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Indexed for the first time in the last N days. If you are looking for fresh files.", None, -1))
        self.FilterIndexedLastDaysEnabled.setText(QtWidgets.QApplication.translate("MainWindow", "Indexed in last", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("MainWindow", "day(s)", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("MainWindow", "Saved filters", None, -1))
        self.FilterListRemoveButton.setText(QtWidgets.QApplication.translate("MainWindow", "-", None, -1))
        self.FilterListSaveButton.setText(QtWidgets.QApplication.translate("MainWindow", "+", None, -1))
        self.FilterListLineEdit.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "New name", None, -1))
        self.tabsSearch.setTabText(self.tabsSearch.indexOf(self.tabMain), QtWidgets.QApplication.translate("MainWindow", "Main", None, -1))
        self.DBRootScanPathLabel.setText(QtWidgets.QApplication.translate("MainWindow", "Scan path: ", None, -1))
        self.DBSettingsLabel.setText(QtWidgets.QApplication.translate("MainWindow", "Database Settings", None, -1))
        self.DBCountLabel.setText(QtWidgets.QApplication.translate("MainWindow", "DB Count ", None, -1))
        self.DBSelectDatabaseLabel.setText(QtWidgets.QApplication.translate("MainWindow", "Select DB: ", None, -1))
        self.DBFileTypeFilter.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "exe,doc,txt (comma as first or last symbol - for \"without extension\")", None, -1))
        self.DBRootScanPath.setItemText(1, QtWidgets.QApplication.translate("MainWindow", "Press to select new path...", None, -1))
        self.DBFileTypeFilterLabel.setText(QtWidgets.QApplication.translate("MainWindow", "File types:", None, -1))
        self.DBFileTypeFilterMode.setItemText(0, QtWidgets.QApplication.translate("MainWindow", "Blacklist", None, -1))
        self.DBFileTypeFilterMode.setItemText(1, QtWidgets.QApplication.translate("MainWindow", "Whitelist", None, -1))
        self.DBApplySettingsButton.setText(QtWidgets.QApplication.translate("MainWindow", "Apply", None, -1))
        self.tabsSearch.setTabText(self.tabsSearch.indexOf(self.tabDatabaseSettings), QtWidgets.QApplication.translate("MainWindow", "Sqlite", None, -1))
        self.MySQLServerAddress.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Server Address", None, -1))
        self.MySQLDBName.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Database Name", None, -1))
        self.MySQLLogin.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Login", None, -1))
        self.MySQLPassword.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Password", None, -1))
        self.MySQLTestButton.setText(QtWidgets.QApplication.translate("MainWindow", "Test connection", None, -1))
        self.MySQLServerPort.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "port", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("MainWindow", ":", None, -1))
        self.MySQLInitDBButton.setText(QtWidgets.QApplication.translate("MainWindow", "Init DB", None, -1))
        self.MySQLPathsTable.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "Directories", None, -1))
        self.MySQLPathsTableAddButton.setText(QtWidgets.QApplication.translate("MainWindow", "Add...", None, -1))
        self.MySQLPathsTableRemoveButton.setText(QtWidgets.QApplication.translate("MainWindow", "Remove", None, -1))
        self.tabsSearch.setTabText(self.tabsSearch.indexOf(self.tabMySQL), QtWidgets.QApplication.translate("MainWindow", "MySQL", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "&File", None, -1))
        self.menuHelp.setTitle(QtWidgets.QApplication.translate("MainWindow", "&Help", None, -1))
        self.actionStartScan.setText(QtWidgets.QApplication.translate("MainWindow", "Start Indexing", None, -1))
        self.actionPreferences.setText(QtWidgets.QApplication.translate("MainWindow", "Preferences...", None, -1))
        self.actionPreferences.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+P", None, -1))
        self.actionShowHelpInfo.setText(QtWidgets.QApplication.translate("MainWindow", "Show Manual", None, -1))
        self.actionAbout.setText(QtWidgets.QApplication.translate("MainWindow", "About", None, -1))
        self.actionExit.setText(QtWidgets.QApplication.translate("MainWindow", "Exit", None, -1))
        self.actionExit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Q", None, -1))
        self.actionShowLog.setText(QtWidgets.QApplication.translate("MainWindow", "Show Log", None, -1))
        self.actionOpenWorkingDirectory.setText(QtWidgets.QApplication.translate("MainWindow", "Open Working Directory", None, -1))

import icons_rc
