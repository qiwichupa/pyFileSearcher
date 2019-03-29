# If you want to use it with python <3.6 and PySide:
# - replace "QtWidgets." with "QtGui."
# - replace "PySide2" with "PySide" (also in "icons_rc.py")
# - remove "import PySide2.QtWidgets as QtWidgets"
# - in "utilities.py" replace "from os import scandir" with "from scandir import scandir" (and install scandir module)
# - resave UI files with Qt Designer and pyside utils


import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets
import send2trash

# About this one.
# With python 3.7, PySide2 AND mysql.connector (https://pypi.org/project/mysql-connector-python/) - I have memory leak in scan thread.
# So I prefer mysqlclient (MySQLdb fork - https://pypi.org/project/mysqlclient) - it's fully compatible.
# But with python 3.4 and PySide - for win 2003 server build -  mysql.connector works fine,
# and mysqlclient is difficult to install. So I leave both of it here.
import MySQLdb as my_sql
# import mysql.connector as my_sql


import csv
import datetime
import logging
import os
import pathlib
import platform
import random
import re
import sqlite3
import subprocess
import sys
import time

from hashlib import md5

import utilities

from ui_files import pyMain
from ui_files import pyPreferences
from ui_files import pyAbout
from ui_files import pyManual
from ui_files import pyLogViewer
from ui_files import pyFolderSize

__appname__ = "pyFileSearcher"
__version__ = "1.0.0-devel10"

# get path of program dir.
# sys._MEIPASS - variable of pyinstaller (one-dir package) with path to executable
try:
    sys._MEIPASS
    appPath = sys._MEIPASS
except:
    appPath =  os.path.dirname(os.path.abspath(__file__))

# set "data" in program dir as working directory
appDataPath = os.path.join(appPath, "data")
try:
    os.makedirs(appDataPath, exist_ok=True)
except:
    appDataPath = appPath

scanPIDFile = os.path.join(appDataPath, "scan.pid")
logfile = os.path.join(appDataPath, "pyfilesearcher.log")

# remove large logfile
logFileSizeLimit = 8 # MB
try:
    os.stat(logfile).st_size
    if os.stat(logfile).st_size > logFileSizeLimit*1024**2:
        removedLogFileSize = os.stat(logfile).st_size
        try:
            os.remove(logfile)
        except:
            pass
except:
    pass

# logging
logging.basicConfig(handlers=[logging.FileHandler(logfile, 'a', 'utf-8-sig')],
                    format="%(asctime)-15s\t%(name)-10s\t%(levelname)-8s\t%(module)-10s\t%(funcName)-35s\t%(lineno)-6d\t%(message)s",
                    level=logging.DEBUG)
logger = logging.getLogger(name="main-gui")
sys.stdout = utilities.LoggerWriter(logger.warning)
sys.stderr = utilities.LoggerWriter(logger.warning)
try:
    removedLogFileSize
    logger.info("Previous logfile was removed by size limit (" + str(logFileSizeLimit) + "MB). Size was: " + str(removedLogFileSize) + " bytes.")
except:
    pass

# platform check
if platform.system() == "Linux":
    isLinux = True
    isWindows = False
elif platform.system() == "Windows":
    isWindows = True
    isLinux = False
else:
    logger.critical("This app is for only Linux and Windows, sorry!")
    sys.exit(1)

# scan mode
if len(sys.argv) <= 1 or sys.argv[1] != "--scan":
    isScanMode = False
else:
    isScanMode = True

# MAIN APPLICATION CLASS
class Main(QtWidgets.QMainWindow, pyMain.Ui_MainWindow):
    #sigUpdateDB = QtCore.Signal(str)
    checkingFileExistenceThreads = {}
    dbConn = {}
    tableFilesItemDelegates = {}


    tableFilesColumnNumIndx = 0
    tableFilesColumnFilnameIndx = 1
    tableFilesColumnTypeIndx = 2
    tableFilesColumnSizeIndx = 3
    tableFilesColumnModifiedIndx = 4
    tableFilesColumnIndexedIndx = 5
    tableFilesColumnCreatedIndx = 6
    tableFilesColumnPathIndx = 7

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " (v. " + __version__ + ")")

        self.clip = QtWidgets.QApplication.clipboard()

        self.settings = QtCore.QSettings(os.path.join(appDataPath, "settings.ini"), QtCore.QSettings.IniFormat)
        self.settings.setIniCodec("UTF-8")

        ## Menu items
        self.actionPreferences.triggered.connect(self.actionPreferencesEmitted)
        self.actionStartScan.triggered.connect(self.updateDBEmitted)
        self.actionAbout.triggered.connect(self.actionAboutEmitted)
        self.actionShowHelpInfo.triggered.connect(self.actionShowHelpInfoEmitted)
        self.actionExit.triggered.connect(self.exitActionTriggered)
        self.actionShowLog.triggered.connect(self.actionShowLogEmitted)
        self.actionOpenWorkingDirectory.triggered.connect(self.actionOpenWorkingDirectoryEmitted)

        ## Commands menu
        self.menuCommands.aboutToShow.connect(self.setCommandsMenu)
        self.cmdOpenFolder.triggered.connect(self.menuOpenFolder)
        self.cmdMoveFilesToTrash.triggered.connect(self.menuDeleteFiles)
        self.cmdCopySelectedToClipboard.triggered.connect(self.menuCopySelectedToClipboard)
        self.cmdExportSelectedToCSV.triggered.connect(self.menuExportSelectedToCsv)
        self.cmdExportAllToCSV.triggered.connect(self.menuExportAllToCsv)
        self.cmdCalculateFolderSize.triggered.connect(self.menuCalculateFolderSize)

        ## Tools menu
        self.toolsFolderSize.triggered.connect(self.folderSizeEmitted)

        ## Search Tab
        self.FilterSearchInRemoved.toggled.connect(self.filterSearchInRemovedToggled)

        FilterFilenameValidator = QtGui.QRegExpValidator(QtCore.QRegExp("([^\\\/:<>|])*"), self) # i don't know why this "^\\\" works as "not a '\'", but it works -_-
        self.FilterFilename.setValidator(FilterFilenameValidator)
        self.FilterFilename.textEdited.connect(self.filterFilenameTextChanged)
        FilterFileTypesValidator = QtGui.QRegExpValidator(QtCore.QRegExp("([a-z0-9]{1,8},)*"), self)
        self.FilterFileTypes.setValidator(FilterFileTypesValidator)

        self.FilterFilename.returnPressed.connect(self.btnSearchEmitted)
        self.FilterPath.returnPressed.connect(self.btnSearchEmitted)
        self.FilterFileTypes.returnPressed.connect(self.btnSearchEmitted)
        self.btnSearch.clicked.connect(self.btnSearchEmitted)
        self.btnSearch.setDisabled(True)

        self.FilterShowMoreResultsCheckbox.setVisible(False)

        self.tableFiles.setColumnWidth(self.tableFilesColumnNumIndx, 40)
        self.tableFiles.setColumnWidth(self.tableFilesColumnTypeIndx, 50)
        self.tableFiles.setColumnWidth(self.tableFilesColumnModifiedIndx, 150)
        self.tableFiles.setColumnWidth(self.tableFilesColumnCreatedIndx, 150)
        self.tableFiles.setColumnWidth(self.tableFilesColumnIndexedIndx, 150)
        self.tableFiles.setColumnWidth(self.tableFilesColumnFilnameIndx, 200)
        self.tableFiles.contextMenuEvent = self.openContextCommandMenu

        self.tableFiles.cellEntered.connect(self.tableFilesScrolled)
        self.tableFiles.cellClicked.connect(self.checkFilesExistence)

        # delegate must be class-wide for python 3.4 and works fine as local with 3.7 O_o
        self.tableFilesItemDelegates["Size"] = SizeItemDelegate()
        self.tableFiles.setItemDelegateForColumn(self.tableFilesColumnSizeIndx, self.tableFilesItemDelegates["Size"])

        # rename ctime column in linux because it's not a creation time in that case
        if isLinux:
            self.tableFiles.setHorizontalHeaderItem(self.tableFilesColumnCreatedIndx, QtWidgets.QTableWidgetItem("Linux ctime"))

        ## Search Tab - Filter List
        FilterListLineEditalidator = QtGui.QRegExpValidator(QtCore.QRegExp("([a-z0-9_ -])*"), self)
        self.FilterListLineEdit.setValidator(FilterListLineEditalidator)

        self.FilterListSaveButton.setDisabled(True)

        self.FilterListLineEdit.textEdited.connect(self.filterListLineEditEditedEmitted)

        self.FilterListSaveButton.clicked.connect(self.filterListSaveButtonEmitted)
        self.FilterListRemoveButton.clicked.connect(self.filterListRemoveButtonEmitted)
        self.FilterListComboBox.activated.connect(self.filterListComboBoxEmitted)

        ## Database Tab
        DBFileTypeFilterValidator = QtGui.QRegExpValidator(QtCore.QRegExp("(^[,])?([a-z0-9]{1,8},)*"), self)
        self.DBFileTypeFilter.setValidator(DBFileTypeFilterValidator)

        self.DBSelectDatabase.activated.connect(self.selectSqliteDB)
        self.DBCount.valueChanged.connect(self.dbCountEmitted)

        self.DBFileTypeFilter.textEdited.connect(self.dbFileTypeFilterEmitted)
        self.DBFileTypeFilterMode.activated.connect(self.dbFileTypeFilterModeEmitted)
        self.DBRootScanPath.activated.connect(self.dbRootScanPathEmitted)

        self.DBApplySettingsButton.setDisabled(True)
        self.DBApplySettingsButton.clicked.connect(self.dbApplySettingsButtonEmitted)

        ## MySQL tab
        self.MySQLServerAddress.textEdited.connect(self.mySQLServerAddressEmitted)
        self.MySQLServerPort.textEdited.connect(self.mySQLServerPortEmitted)
        self.MySQLDBName.textEdited.connect(self.mySQLDBNameEmitted)
        self.MySQLLogin.textEdited.connect(self.mySQLLoginEmitted)
        self.MySQLPassword.textEdited.connect(self.mySQLPasswordEmitted)

        self.MySQLTestButton.clicked.connect(self.mySQLTestButtonEmitted)
        self.MySQLInitDBCheckBox.toggled.connect(self.MySQLInitDBButton.setEnabled)
        self.MySQLInitDBButton.clicked.connect(self.mySQLInitDBButtonEmitted)

        self.MySQLPathsTableAddButton.clicked.connect(self.mySQLPathsTableAddButtonEmitted)
        self.MySQLPathsTableRemoveButton.clicked.connect(self.mySQLPathsTableRemoveButtonEmitted)

        self.MySQLPathsTable.itemSelectionChanged.connect(self.mySQLPathsTableItemSelectionChanged)

        ## Load Settings
        self.loadInitialSettings()

        ## Checking pid file of indexing process for locking some parts of interface
        self.loadPidChecker()

        ## run scan with --scan parameter
        if isScanMode:
            logger.info("Scan is running with command promt parameter!")
            self.updateDBEmitted()

    def keyPressEvent(self, e):
        """Key mods"""
        if (e.modifiers() & QtCore.Qt.ControlModifier): # CTRL+...

            if e.key() == QtCore.Qt.Key_C:  # CTRL+C
                self.copySelectedToClipboard()

    def loadInitialSettings(self):
        """Load initial settings from configuration file and database"""

        if not self.settings.value("LogLevel"):
            self.settings.setValue("LogLevel", "INFO")
        if not self.settings.value("sqlTransactionLimit"):
            self.settings.setValue("sqlTransactionLimit", "20000")
        if not self.settings.value("SaveRemovedFilesForDays"):
            self.settings.setValue("SaveRemovedFilesForDays", "1")
        if not self.settings.value("DBCount"):
            self.settings.setValue("DBCount", "1")
        if not self.settings.value("useExternalDatabase"):
            self.settings.setValue("useExternalDatabase", "False")
        if not self.settings.value("disableWindowsLongPathSupport"):
            self.settings.setValue("disableWindowsLongPathSupport", "False")
        if not self.settings.value("maxSearchResults"):
            self.settings.setValue("maxSearchResults", "1000")
        if not self.settings.value("filters"):
            self.settings.setValue("filters", "")

        self.refreshSQLTabs()

        self.applyLoggingLevel()

        if self.settings.value("filters") == "":
            self.filters = []
        else:
            self.filters = self.settings.value("filters").split(",")
            for filter in self.filters:
                self.FilterListComboBox.addItems([filter])

        if isWindows and not utilities.str2bool(self.settings.value("disableWindowsLongPathSupport")):
            self.windowsLongPathHack = True
        else:
            self.windowsLongPathHack = False

        DBCount = int(self.settings.value("DBCount"))

        for DBNumber in range(1, DBCount + 1):
            if not os.path.isfile(get_db_path(DBNumber)):
                self.createSqliteDB(DBNumber)

            if self.selectSqliteDB(DBNumber, False):
                self.DBSelectDatabase.addItem("DB" + str(DBNumber))
                self.DBSelectDatabase.setCurrentIndex(DBNumber - 1)
        self.DBCount.setValue(DBCount)

        # Mysql
        if not self.settings.value("MySQL/MySQLServerPort"):
            self.settings.setValue("MySQL/MySQLServerPort", "3306")

        self.MySQLServerAddress.setText(self.settings.value("MySQL/MySQLServerAddress"))
        self.MySQLServerPort.setText(self.settings.value("MySQL/MySQLServerPort"))
        self.MySQLDBName.setText(self.settings.value("MySQL/MySQLDBName"))
        self.MySQLLogin.setText(self.settings.value("MySQL/MySQLLogin"))
        self.MySQLPassword.setText(self.settings.value("MySQL/MySQLPassword"))

        directoriesCount = self.settings.beginReadArray("MySQL/_Directories")

        for i in range(directoriesCount):
            row = self.MySQLPathsTable.rowCount()
            self.settings.setArrayIndex(i)
            dir = self.settings.value("directory")

            self.MySQLPathsTable.insertRow(row)
            self.MySQLPathsTable.setItem(row - 1, 1, QtWidgets.QTableWidgetItem(dir))
        self.settings.endArray()

        self.mySQLPathsTableItemSelectionChanged()

    # MAIN MENU ACTIONS
    #
    def actionPreferencesEmitted(self):
        """Opens the preferences dialog"""
        initValues = {"useExternalDatabase": self.settings.value("useExternalDatabase"),
                      "disableWindowsLongPathSupport": self.settings.value("disableWindowsLongPathSupport"),
                      "maxSearchResults": self.settings.value("maxSearchResults"),
                      "LogLevel": self.settings.value("LogLevel"),
                      "SaveRemovedFilesForDays": self.settings.value("SaveRemovedFilesForDays"),
                      "sqlTransactionLimit": self.settings.value("sqlTransactionLimit")
                      }
        dialog = PreferencesDialog(initValues)
        if dialog.exec_():
            self.settings.setValue("useExternalDatabase", utilities.bool2str(dialog.PREFUseExternalDB.isChecked()))
            self.settings.setValue("disableWindowsLongPathSupport",
                                   utilities.bool2str(dialog.PREFDisableWindowsLongPathSupport.isChecked()))
            self.settings.setValue("maxSearchResults", str(dialog.PREFMaxSearchResults.value()))
            self.settings.setValue("LogLevel", dialog.PREFLoggingLevel.currentText())
            self.settings.setValue("SaveRemovedFilesForDays", dialog.PREFSaveRemovedInfoDays.value())
            self.settings.setValue("sqlTransactionLimit", dialog.PREFsqlTransactionLimit.value())

            self.refreshSQLTabs()
            self.applyLoggingLevel()

    def updateDBEmitted(self):
        """Starts the file system scan. Depending on the settings, it generates scanning threads of either
            an internal or external database. For each thread, an updateDBThreads element is created, which is
            subsequently deleted to determine the end of the scan."""
        logger.info(">> INDEXING STARTED. Creating PID-file: " + scanPIDFile)
        os.close(os.open(scanPIDFile, os.O_CREAT))

        self.updateDBThreads = {}

        if self.settings.value("useExternalDatabase") == "False":
            self.DBScanEngine = "Sqlite"
            for DBNumber in range(1, self.DBCount.value() + 1):
                self.updateDBThreads[DBNumber] = UpdateSqliteDBThread(DBNumber, self.settings)
                self.updateDBThreads[DBNumber].sigIsOver.connect(self.removeScanThreadWhenThreadIsOver)
                self.updateDBThreads[DBNumber].start()
        else:
            self.DBScanEngine = "MySQL"
            self.newRemovedKey = self.mysql_prepare_db_for_update()
            if self.newRemovedKey:
                for row in range(0, self.MySQLPathsTable.rowCount()):
                    path = self.MySQLPathsTable.item(row, 0).text()
                    self.updateDBThreads[row] = UpdateMysqlDBThread(path, row, self.newRemovedKey, self.settings)
                    self.updateDBThreads[row].sigIsOver.connect(self.removeScanThreadWhenThreadIsOver)
                    self.updateDBThreads[row].start()
            else:
                logger.critical("Scan was interrupted by MySQL connection error")
                os.remove(scanPIDFile)
                if isScanMode:
                    logger.info("isScanMode - exit app")
                    self.exitActionTriggered()

    def actionAboutEmitted(self):
        """Shows about dialog"""
        dialog = AboutDialog()
        dialog.pushButton.clicked.connect(dialog.close)
        dialog.exec_()

    def folderSizeEmitted(self):
        """Shows folder size tool dialog"""
        dialog = FolderSizeDialog()
        #self.fsdialog.path.connect(self.get_folder_size_and_files_count)
        if dialog.exec_():
            dir = dialog.linePath.text().strip()
            result = self.get_folder_size_and_files_count(dir)
            logger.info("Get size of folder(" + dir + "): " + str(result["size"]) + " byte(s) in " + str(result["filesCount"]) + " file(s)")
            QtWidgets.QMessageBox.information(self, __appname__ + " - folder info",
                                              "Folder: " + dir +
                                              "\n\nTotal size: " + utilities.get_humanized_size(result["size"]) + " (" + str(result["size"]) + ")" +
                                              "\n\nTotal files:  " + str(result["filesCount"])
                                              )

    def actionShowHelpInfoEmitted(self):
        """Shows help dialog"""
        dialog = HelpDialog()
        dialog.pushButton.clicked.connect(dialog.close)
        dialog.exec_()

    def actionShowLogEmitted(self):
        """Shows log-file content"""
        dialog = ShowLogDialog()
        dialog.exec_()

    def actionOpenWorkingDirectoryEmitted(self):
        """Opens working directory (appDataPath)"""
        if isWindows:
            try:
                os.startfile(appDataPath)
            except Exception as e:
                logger.warning("Opening directory error: \n" + str(e))
                QtWidgets.QMessageBox.warning(self, __appname__, "Opening directory error: " + str(e))
        else:
            try:
                subprocess.check_call(["xdg-open", appDataPath], stderr=subprocess.STDOUT)

            except subprocess.CalledProcessError as e:
                logger.warning("Opening directory error: " + str(e))
                QtWidgets.QMessageBox.warning(self, __appname__, "Opening directory error: " + str(e))

    #
    # MAIN MENU ACTIONS - END SECTION

    # SAVE/LOAD FILTERS
    #
    def filterListSaveButtonEmitted(self):
        """Saves the current search settings as a new preset, or updates an existing preset."""
        filterName = self.FilterListLineEdit.text()
        if filterName not in self.filters:
            self.filters += [filterName]
            self.FilterListComboBox.addItems([filterName])
            self.FilterListRemoveButton.setEnabled(True)

        self.settings.setValue("FILTER_" + filterName + "/FilterFilename", self.FilterFilename.text())
        self.settings.setValue("FILTER_" + filterName + "/FilterPath", self.FilterPath.text())
        self.settings.setValue("FILTER_" + filterName + "/FilterFileTypes", self.FilterFileTypes.text())
        self.settings.setValue("FILTER_" + filterName + "/FilterMinSize", self.FilterMinSize.value())
        self.settings.setValue("FILTER_" + filterName + "/FilterMinSizeType", self.FilterMinSizeType.currentIndex())
        self.settings.setValue("FILTER_" + filterName + "/FilterMinSizeEnabled", self.FilterMinSizeEnabled.isChecked())
        self.settings.setValue("FILTER_" + filterName + "/FilterMaxSize", self.FilterMaxSize.value())
        self.settings.setValue("FILTER_" + filterName + "/FilterMaxSizeType", self.FilterMaxSizeType.currentIndex())
        self.settings.setValue("FILTER_" + filterName + "/FilterMaxSizeEnabled", self.FilterMaxSizeEnabled.isChecked())
        self.settings.setValue("FILTER_" + filterName + "/FilterIndexedLastDays", self.FilterIndexedLastDays.value())
        self.settings.setValue("FILTER_" + filterName + "/FilterIndexedLastDaysEnabled", self.FilterIndexedLastDaysEnabled.isChecked())
        self.settings.setValue("FILTER_" + filterName + "/FilterSearchInRemoved", self.FilterSearchInRemoved.isChecked())

        self.settings.setValue("filters", ",".join(self.filters))

        self.FilterListLineEdit.setText("")

        # setCurrentIndex instead of setCurrentText - for backward compatibility with pyside|qt4
        listIndex = self.FilterListComboBox.findText(filterName)
        self.FilterListComboBox.setCurrentIndex(listIndex)
        self.FilterListSaveButton.setDisabled(True)

    def filterListComboBoxEmitted(self):
        """Loads the search preset"""

        if self.FilterListComboBox.currentIndex() == 0:
            self.FilterListLineEdit.setText("")
            self.FilterListSaveButton.setDisabled(True)
            self.FilterListRemoveButton.setDisabled(True)
            return

        filterName = self.FilterListComboBox.currentText()

        self.FilterFilename.setText(self.settings.value("FILTER_" + filterName + "/FilterFilename"))
        self.FilterPath.setText(self.settings.value("FILTER_" + filterName + "/FilterPath"))
        self.FilterFileTypes.setText(self.settings.value("FILTER_" + filterName + "/FilterFileTypes"))
        self.FilterMinSize.setValue(int(self.settings.value("FILTER_" + filterName + "/FilterMinSize")))
        self.FilterMinSizeType.setCurrentIndex(int(self.settings.value("FILTER_" + filterName + "/FilterMinSizeType")))
        self.FilterMinSizeEnabled.setChecked(
            utilities.str2bool(self.settings.value("FILTER_" + filterName + "/FilterMinSizeEnabled")))
        self.FilterMaxSize.setValue(int(self.settings.value("FILTER_" + filterName + "/FilterMaxSize")))
        self.FilterMaxSizeType.setCurrentIndex(int(self.settings.value("FILTER_" + filterName + "/FilterMaxSizeType")))
        self.FilterMaxSizeEnabled.setChecked(
            utilities.str2bool(self.settings.value("FILTER_" + filterName + "/FilterMaxSizeEnabled")))
        self.FilterIndexedLastDays.setValue(int(self.settings.value("FILTER_" + filterName + "/FilterIndexedLastDays")))
        self.FilterIndexedLastDaysEnabled.setChecked(
            utilities.str2bool(self.settings.value("FILTER_" + filterName + "/FilterIndexedLastDaysEnabled")))
        self.FilterSearchInRemoved.setChecked(
            utilities.str2bool(self.settings.value("FILTER_" + filterName + "/FilterSearchInRemoved")))

        self.filterFilenameTextChanged()

        self.FilterListLineEdit.setText(filterName)
        self.FilterListSaveButton.setEnabled(True)
        self.FilterListRemoveButton.setEnabled(True)

    def filterListLineEditEditedEmitted(self):
        """Disables the save preset button if the preset name is not specified."""
        if self.FilterListLineEdit.text() == "":
            self.FilterListSaveButton.setDisabled(True)
        else:
            self.FilterListSaveButton.setEnabled(True)

    def filterListRemoveButtonEmitted(self):
        """Deletes the selected preset."""
        filterName = self.FilterListComboBox.currentText()

        self.filters.remove(filterName)
        self.FilterListComboBox.removeItem(self.FilterListComboBox.currentIndex())
        self.settings.remove("FILTER_" + filterName)
        self.settings.setValue("filters", ",".join(self.filters))
        if len(self.filters) == 0:
            self.FilterListRemoveButton.setDisabled(True)

    #
    # SAVE/LOAD FILTERS - END SECTION

    # MySQL THINGS
    #
    def mySQLServerAddressEmitted(self):
        """Saves MySQL server address to settings"""
        self.settings.setValue("MySQL/MySQLServerAddress", self.MySQLServerAddress.text())

    def mySQLServerPortEmitted(self):
        """Saves MySQL server port to settings"""
        self.settings.setValue("MySQL/MySQLServerPort", self.MySQLServerPort.text())

    def mySQLDBNameEmitted(self):
        """Saves MySQL database name to settings"""
        self.settings.setValue("MySQL/MySQLDBName", self.MySQLDBName.text())

    def mySQLLoginEmitted(self):
        """Saves MySQL login to settings"""
        self.settings.setValue("MySQL/MySQLLogin", self.MySQLLogin.text())

    def mySQLPasswordEmitted(self):
        """Saves MySQL password to settings"""
        self.settings.setValue("MySQL/MySQLPassword", self.MySQLPassword.text())

    def mySQLTestButtonEmitted(self):
        """Tries to establish a connection to the server.
            Upon successful connection, the database initialization option is active."""

        self.MySQLTestButton.setDisabled(True)
        try:
            dbConn = my_sql.connect(
                host=self.MySQLServerAddress.text(),
                port=int(self.MySQLServerPort.text()),
                user=self.MySQLLogin.text(),
                passwd=self.MySQLPassword.text(),
                db=self.MySQLDBName.text(),
                charset="utf8")
        except Exception as e:
            logger.critical("Connection error: " + str(e))
            if isScanMode == False:
                QtWidgets.QMessageBox.critical(self, "MySQL Error", "Connection error: " + str(e))
            self.MySQLTestButton.setStyleSheet('QPushButton {}')
            self.MySQLTestButton.setText("Test connection")

            self.MySQLInitDBCheckBox.setDisabled(True)
        else:
            self.MySQLTestButton.setStyleSheet('QPushButton {color: green;}')
            self.MySQLTestButton.setText("Connected.")
            self.MySQLInitDBCheckBox.setEnabled(True)
        finally:
            self.MySQLTestButton.setEnabled(True)

    def mySQLInitDBButtonEmitted(self):
        """Database initialization. A table is created. If the table already exists, it will be deleted and re-created."""
        try:
            dbConn = my_sql.connect(
                host=self.MySQLServerAddress.text(),
                port=int(self.MySQLServerPort.text()),
                user=self.MySQLLogin.text(),
                passwd=self.MySQLPassword.text(),
                db=self.MySQLDBName.text(),
                charset="utf8")
        except Exception as e:
            logger.critical("Connection error: " + str(e))
            if isScanMode == False:
                QtWidgets.QMessageBox.critical(self, "MySQL Error", "Connection error: " + str(e))
        else:
            dbCursor = dbConn.cursor()
            dbCursor.execute("DROP TABLE IF EXISTS Files")
            dbCursor.execute("""CREATE TABLE IF NOT EXISTS Files(
                                hash CHAR(32), 
                                removed TINYINT(1),
                                filename VARCHAR(300),
                                type VARCHAR(8),  
                                path VARCHAR(2000), 
                                size BIGINT, 
                                created INT, modified INT, 
                                indexed INT,
                                UNIQUE KEY hash_type (hash, type),
                                INDEX size_indexed_type (size, indexed, type),
                                INDEX indexed_size_type (indexed, size, type),
                                INDEX type_size_indexed (type, size, indexed),
                                INDEX path (path),
                                INDEX removed (removed)
                                )
                                PARTITION BY RANGE COLUMNS (type)  (
                                PARTITION p0 VALUES LESS THAN ('a'),
                                PARTITION p1 VALUES LESS THAN ('b'),
                                PARTITION p2 VALUES LESS THAN ('c'),
                                PARTITION p3 VALUES LESS THAN ('d'),
                                PARTITION p4 VALUES LESS THAN ('e'),
                                PARTITION p5 VALUES LESS THAN ('f'),
                                PARTITION p6 VALUES LESS THAN ('g'),
                                PARTITION p7 VALUES LESS THAN ('h'),
                                PARTITION p8 VALUES LESS THAN ('i'),
                                PARTITION p9 VALUES LESS THAN ('j'),
                                PARTITION p10 VALUES LESS THAN ('k'),
                                PARTITION p11 VALUES LESS THAN ('l'),
                                PARTITION p12 VALUES LESS THAN ('m'),
                                PARTITION p13 VALUES LESS THAN ('n'),
                                PARTITION p14 VALUES LESS THAN ('o'),
                                PARTITION p15 VALUES LESS THAN ('p'),
                                PARTITION p16 VALUES LESS THAN ('q'),
                                PARTITION p17 VALUES LESS THAN ('r'),
                                PARTITION p18 VALUES LESS THAN ('s'),
                                PARTITION p19 VALUES LESS THAN ('t'),
                                PARTITION p20 VALUES LESS THAN ('u'),
                                PARTITION p21 VALUES LESS THAN ('v'),
                                PARTITION p22 VALUES LESS THAN ('w'),
                                PARTITION p23 VALUES LESS THAN ('x'),
                                PARTITION p24 VALUES LESS THAN ('y'),
                                PARTITION p25 VALUES LESS THAN ('z'),
                                PARTITION p26 VALUES LESS THAN (MAXVALUE)
                                );
                                """)
            dbConn.commit()
            self.MySQLInitDBButton.setText("Complete!")
            self.MySQLInitDBCheckBox.setChecked(False)

    def mySQLPathsTableAddButtonEmitted(self):
        """Opens the directory selection dialog. The selected directory is added
           to the list, after which the entire list is saved in the settings file."""
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory", ".")
        if path:
            path = QtCore.QDir.toNativeSeparators(path)
            row = self.MySQLPathsTable.rowCount()
            self.MySQLPathsTable.insertRow(row)
            self.MySQLPathsTable.setItem(row - 1, 1, QtWidgets.QTableWidgetItem(str(path)))

            self.settings.beginWriteArray("MySQL/_Directories")
            for i in range(0, self.MySQLPathsTable.rowCount()):
                self.settings.setArrayIndex(i)
                self.settings.setValue("directory", [self.MySQLPathsTable.item(i, 0).text()])
            self.settings.endArray()

    def mySQLPathsTableRemoveButtonEmitted(self):
        """Removes the selected directory from the list of directories,
           after which the list of directories is saved in the settings file"""
        if self.MySQLPathsTable.selectedItems():
            currItem = self.MySQLPathsTable.currentItem()
            row = self.MySQLPathsTable.row(currItem)
            self.MySQLPathsTable.removeRow(row)

            self.settings.beginWriteArray("MySQL/_Directories")
            for i in range(0, self.MySQLPathsTable.rowCount()):
                self.settings.setArrayIndex(i)
                self.settings.setValue("directory", [self.MySQLPathsTable.item(i, 0).text()])
            self.settings.endArray()

    def mySQLPathsTableItemSelectionChanged(self):
        """Checks for the presence of selected lines in the directory list.
           If something is selected, the delete button becomes active."""
        if self.MySQLPathsTable.selectedItems():
            self.MySQLPathsTableRemoveButton.setEnabled(True)
        else:
            self.MySQLPathsTableRemoveButton.setDisabled(True)

    def mysqlEstablishConnection(self):
        """Connect to MySQL for work purposes"""
        try:
            self.dbConnMysql = my_sql.connect(
                host=self.MySQLServerAddress.text(),
                port=int(self.MySQLServerPort.text()),
                user=self.MySQLLogin.text(),
                passwd=self.MySQLPassword.text(),
                db=self.MySQLDBName.text())
        except Exception as e:
            logger.critical("mysql error connection error: " + str(e))
            raise Exception

    def mysql_prepare_db_for_update(self):
        """If there is - selects the first value of the column 'removed' and generates a random new one
            and return it. When scanning, this value is set for all new or updated rows in the
            database to identify deleted files and process them in mysqlPostUpdateProcedure."""
        try:
            self.mysqlEstablishConnection()
        except:
            # this will cancel the creation of scan threads
            return False

        cursor = self.dbConnMysql.cursor()
        logger.info("MySQL preparation...")

        try:
            cursor.execute("SELECT removed FROM Files LIMIT 1")
            oldRemovedKey = cursor.fetchone()[0]

        except:
            r = range(0, 100)
            logger.warning("...old removed key not found, it's ok while first run...")
        else:
            logger.debug("...old removed key is: " + str(oldRemovedKey) + "...")
            r = list(range(0, int(oldRemovedKey))) + list(range(int(oldRemovedKey) + 1, 100))

        newRemovedKey = random.choice(r)
        logger.debug("...new removed key is: " + str(newRemovedKey) + "...")

        self.dbConnMysql.close()
        logger.info("MySQL preparation complete!")
        return newRemovedKey

    def mysqlPostUpdateProcedure(self):
        """Depends on 'SaveRemovedFilesForDays' settings value:
           deletes all rows whose column 'removed' value is different from the one selected in the mysql_prepare_db_for_update,
           or marks that rows by -1 value for 'removed' and cleanups db from old removed file records """
        try:
            self.mysqlEstablishConnection()
        except:
            logger.warning("MySQL connection error in post-update procedure")
            return

        cursor = self.dbConnMysql.cursor()
        logger.info("MySQL post-update procedure...")
        logger.info("...removing deleted files from DB...")
        currentTime = int(time.time())
        SaveRemovedFilesForDaysInSec = int(self.settings.value("SaveRemovedFilesForDays")) * 86400
        removedTime = currentTime - SaveRemovedFilesForDaysInSec
        try:
            if int(self.settings.value("SaveRemovedFilesForDays")) != 0:
                cursor.execute("UPDATE Files SET removed=%s, indexed=%s WHERE removed <> %s AND removed <> %s", (-1, currentTime, self.newRemovedKey, -1))
                self.dbConnMysql.commit()
                removedCounter = cursor.rowcount
                logger.info("...files set as removed: " + str(removedCounter) + " ...")
                cursor.execute("DELETE FROM Files WHERE removed = %s AND indexed < %s", (-1, removedTime))
                self.dbConnMysql.commit()
                cleanCounter = cursor.rowcount
                logger.info("...files removed from db: " + str(cleanCounter) + " ...")
            else:
                logger.debug("...SaveRemovedFilesForDays=0, all removed files will be removed from db ...")
                cursor.execute("DELETE FROM Files WHERE removed <> %s", (self.newRemovedKey,))
                self.dbConnMysql.commit()
                cleanCounter = cursor.rowcount
                logger.info("...files removed from db: " + str(cleanCounter) + " ...")
        except Exception as e:
            logger.warning("...Cleaning DB error: " + str(e))

        self.dbConnMysql.close()
        logger.info("MySQL post-update procedure complete.")

    #
    # MySQL THINGS - END SECTION

    # Sqlite THINGS
    #
    def selectSqliteDB(self, DBNumber, runViaGUI=True):
        """At the time of selecting the internal (sqlite) database loads settings from it."""
        if runViaGUI is True:
            DBNumber = DBNumber + 1

        self.dbConn[DBNumber] = sqlite3.connect(get_db_path(DBNumber))

        try:
            dbCursor = self.dbConn[DBNumber].cursor()

            keys = ("RootPath", "Exclusions", "ExclusionsMode")
            dbOptions = {}
            for key in keys:
                dbOptions[key] = dbCursor.execute("SELECT value FROM Settings WHERE option=?", (key,)).fetchall()[0][0]

            # setCurrentIndex instead of setCurrentText - for backward compatibility with pyside|qt4
            listIndex = self.DBFileTypeFilterMode.findText(dbOptions["ExclusionsMode"])
            self.DBFileTypeFilterMode.setCurrentIndex(listIndex)

            self.DBFileTypeFilter.setText(dbOptions["Exclusions"])
            self.DBRootScanPath.setItemText(0, dbOptions["RootPath"] if dbOptions["RootPath"] else "[Path is not set]")
        except Exception as e:
            logger.critical("Unable to load settings from database:\r\n'" +
                            get_db_path(DBNumber) + "'\r\nError:\r\n" + str(e))
            if isScanMode == False:
                QtWidgets.QMessageBox.critical(self, __appname__, "Unable to load settings from database:\r\n'" +
                                               get_db_path(DBNumber) + "'\r\nError:\r\n" + str(e))
            sys.exit(1)

        self.DBSettingsLabel.setText("Database \"DB" + str(DBNumber) + "\" settings")

        return True

    def createSqliteDB(self, DBNumber):
        """Create new sqlite database with default settings for slot N"""
        dbConn = sqlite3.connect(get_db_path(DBNumber))
        dbCursor = dbConn.cursor()
        dbCursor.execute("""CREATE TABLE IF NOT EXISTS Settings(id INTEGER PRIMARY KEY, 
                                    option TEXT KEY, value TEXT)""")
        dbCursor.execute("""INSERT INTO Settings VALUES(?, ?, ?)""", (None, "RootPath", ""))
        dbCursor.execute("""INSERT INTO Settings VALUES(?, ?, ?)""", (None, "Exclusions", ""))
        dbCursor.execute("""INSERT INTO Settings VALUES(?, ?, ?)""", (None, "ExclusionsMode", "Blacklist"))

        dbCursor.execute("""CREATE TABLE IF NOT EXISTS Files(hash TEXT UNIQUE, removed TEXT,
                            filename TEXT, path TEXT, size INT, created INT, modified INT, indexed INT)""")

        dbConn.commit()

    def removeSqliteDB(self, DBNumber):
        """Delete connection to database and database file"""
        del self.dbConn[DBNumber]
        try:
            os.remove(get_db_path(DBNumber))
        except Exception as e:
            logger.critical("Unable to remove database file:\r\n'" +
                            get_db_path(DBNumber) + "'\r\nError:\r\n" + str(e))
            if isScanMode == False:
                QtWidgets.QMessageBox.critical(self, __appname__, "Unable to remove database file:\r\n'" +
                                               get_db_path(DBNumber) + "'\r\nError:\r\n" + str(e))
            sys.exit(1)

    def dbCountEmitted(self, newDBCount):
        """Looks at the settings and compares the number of internal databases specified in them with
            the value again specified via the interface. Starts the creation or deletion of databases."""
        newDBCount = self.DBCount.value()
        oldDBCount = int(self.settings.value("DBCount"))
        if newDBCount > oldDBCount:
            for i in range(oldDBCount + 1, newDBCount + 1):
                self.createSqliteDB(i)
                if self.selectSqliteDB(i, False):
                    self.DBSelectDatabase.addItem("DB" + str(i))
                    self.DBSelectDatabase.setCurrentIndex(i - 1)
        elif newDBCount < oldDBCount:
            for i in range(oldDBCount, newDBCount, -1):
                dbForRemove = i
                self.removeSqliteDB(dbForRemove)
                if self.DBSelectDatabase.currentIndex() is dbForRemove - 1:
                    self.selectSqliteDB(self.DBSelectDatabase.currentIndex() - 1)
                self.DBSelectDatabase.removeItem(dbForRemove - 1)
        else:
            pass
        self.settings.setValue("DBCount", newDBCount)

    def dbFileTypeFilterEmitted(self):
        """Sets Apply button active when Exclusions was edited"""
        self.DBApplySettingsButton.setEnabled(True)

    def dbFileTypeFilterModeEmitted(self):
        """Makes Apply button active when ExclusionsMode (Whitelist|Blacklist) was selected"""
        self.DBApplySettingsButton.setEnabled(True)

    def dbRootScanPathEmitted(self):
        """Makes Apply button active when path was selected, and sets path into first slot in combobox"""
        if self.DBRootScanPath.currentIndex() is 1:
            currentPath = self.DBRootScanPath.itemText(0)
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", currentPath)
            if path:
                path = QtCore.QDir.toNativeSeparators(path)
                self.DBRootScanPath.setItemText(0, path)
                self.DBApplySettingsButton.setEnabled(True)
            self.DBRootScanPath.setCurrentIndex(0)

    def dbApplySettingsButtonEmitted(self):
        """Saves internal database settings to it"""
        self.DBSelectDatabase.setDisabled(True)
        currentDB = self.DBSelectDatabase.currentIndex() + 1
        dbSettings = {}
        dbSettings["DBFileTypeFilter"] = self.DBFileTypeFilter.text()
        dbSettings["DBFileTypeFilterMode"] = self.DBFileTypeFilterMode.currentText()
        dbSettings["DBRootScanPath"] = self.DBRootScanPath.itemText(0)

        self.SaveSqliteDBSettingsThread = SaveSqliteDBSettingsThread(currentDB, dbSettings)
        self.SaveSqliteDBSettingsThread.settingsSavedSig.connect(self.saveSqliteDBSettingsThreadSavedSigEmitted)
        self.SaveSqliteDBSettingsThread.start()

    def saveSqliteDBSettingsThreadSavedSigEmitted(self, DBNumber):
        """After saving the settings - rereads the settings of the internal database and unlocks the interface"""
        self.selectSqliteDB(DBNumber, False)
        self.DBSelectDatabase.setEnabled(True)
        self.DBApplySettingsButton.setDisabled(True)
        self.DBSelectDatabase.setFocus()

    #
    # Sqlite THINGS - END SECTION

    # TABLE CONTEXT MENU
    #
    def openContextCommandMenu(self, event):
        """Create context menu for tableFiles widget"""
        self.menuCommands.popup(QtGui.QCursor.pos())

    def setCommandsMenu(self):
        """sets the command menu behavior"""
        if len(self.tableFiles.selectedItems()) > 8 or len(self.tableFiles.selectedItems()) == 0:
            self.cmdOpenFolder.setDisabled(True)
        else:
            self.cmdOpenFolder.setDisabled(False)

        if len(self.tableFiles.selectedItems()) == 0:
            self.cmdMoveFilesToTrash.setDisabled(True)
        else:
            self.cmdMoveFilesToTrash.setDisabled(False)

        if len(self.tableFiles.selectedItems()) == 0:
            self.cmdExportSelectedToCSV.setDisabled(True)
            self.cmdCopySelectedToClipboard.setDisabled(True)
        else:
            self.cmdExportSelectedToCSV.setDisabled(False)
            self.cmdCopySelectedToClipboard.setDisabled(False)

        if self.tableFiles.rowCount() == 0:
            self.cmdExportAllToCSV.setDisabled(True)
        else:
            self.cmdExportAllToCSV.setDisabled(False)

        if len(self.tableFiles.selectedItems()) > 8 or len(self.tableFiles.selectedItems()) == 0:
            self.cmdCalculateFolderSize.setDisabled(True)
        else:
            self.cmdCalculateFolderSize.setDisabled(False)

    def menuOpenFolder(self):
        """Opens folder for selected file"""
        rows = utilities.get_selected_rows_from_qtablewidget(self.tableFiles)

        for row in rows:
            if isWindows:
                try:
                    os.startfile(row[self.tableFilesColumnPathIndx].text())
                except Exception as e:
                    logger.warning("Opening directory error: \n" + str(e))
                    QtWidgets.QMessageBox.warning(self, __appname__, "Opening directory error: " + str(e))
            else:
                try:
                    subprocess.check_call(["xdg-open", row[self.tableFilesColumnPathIndx].text()], stderr=subprocess.STDOUT)

                except subprocess.CalledProcessError as e:
                    logger.warning("Opening directory error: " + str(e))
                    QtWidgets.QMessageBox.warning(self, __appname__, "Opening directory error: " + str(e))

    def menuDeleteFiles(self):
        """Delete selected files"""
        result = QtWidgets.QMessageBox.question(self, __appname__, "Are you sure you want to remove file(s)?", QtWidgets.QMessageBox.Yes
                                                | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)

        if result == QtWidgets.QMessageBox.Yes:
            rows = utilities.get_selected_rows_from_qtablewidget(self.tableFiles)
            errs = []
            for row in rows:
                try:
                    send2trash.send2trash(
                        row[self.tableFilesColumnPathIndx].text() + row[self.tableFilesColumnFilnameIndx].text()
                    )
                except Exception as e:
                    logger.warning("Error while removing file: " + str(e))
                    errs += [str(e)]
            if len(errs) > 0:
                QtWidgets.QMessageBox.warning(self, __appname__, "Error while removing file(s):\n\n" + "\n".join(errs))
            self.checkFilesExistence(forcedCheck=True)

    def menuCopySelectedToClipboard(self):
        """Copy selected to clipboard"""
        self.copySelectedToClipboard()

    def menuExportSelectedToCsv(self):
        """Exports selected rows to csv"""
        csvObj = QtWidgets.QFileDialog.getSaveFileName(parent=None, caption=__appname__ + " - Save as csv",
                                                       directory=".", filter="Simple spreadsheet (*.csv)")
        if csvObj[0]:
            rows = utilities.get_selected_rows_from_qtablewidget(self.tableFiles)
            try:
                with open(csvObj[0], 'w', newline='', encoding='utf-8-sig') as csvfile:
                    csvWriter = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)

                    for row in rows:
                        textRow = []
                        for item in row:
                            textRow += [item.text()]
                        csvWriter.writerow(textRow)
            except Exception as e:
                logger.warning("Error while exporting csv: " + str(e))
                QtWidgets.QMessageBox.warning(self, __appname__, "Error while exporting csv: " + str(e))
        else:
            pass

    def menuExportAllToCsv(self):
        """Exports all search results to csv"""
        self.tableFiles.selectAll()
        self.menuExportSelectedToCsv()

    def menuCalculateFolderSize(self):
        """Shows the total size of the directory and subdirectories, and the total number of files"""
        rows = utilities.get_selected_rows_from_qtablewidget(self.tableFiles)

        for row in rows:
            dir = row[self.tableFilesColumnPathIndx].text()

        result = self.get_folder_size_and_files_count(dir)
        logger.info("Get size of folder(" + dir + "): " + str(result["size"]) + " byte(s) in " + str(result["filesCount"]) + " file(s)")
        QtWidgets.QMessageBox.information(self, __appname__ + " - folder info",
                                          "Folder: " + dir +
                                          "\n\nTotal size: " + utilities.get_humanized_size(result["size"]) + " (" + str(result["size"]) + ")" +
                                          "\n\nTotal files:  " + str(result["filesCount"])
                                          )

    def copySelectedToClipboard(self):
        """Sends selected rows to clipboard as tab-separated text"""
        rows = utilities.get_selected_rows_from_qtablewidget(self.tableFiles)
        strings = []
        for row in rows:
            textRow = []
            for item in row:
                textRow += [item.text()]
            strings += ["\t".join(textRow)]
        result = "\n".join(strings)
        self.clip.setText(result)

    #
    # TABLE CONTEXT MENU - END SECTION

    def removeScanThreadWhenThreadIsOver(self, ThreadNumber):
        """Catching signals of scanning threads. Removes a thread from the list of threads;
        if the list is empty, it starts the cleaning for MySQL and deletes the pid-file."""
        try:
            self.updateDBThreads[ThreadNumber].wait()
            del self.updateDBThreads[ThreadNumber]
        except:
            pass
        logger.info("Scan thread #" + str(ThreadNumber) + " is over.")
        if len(self.updateDBThreads) == 0:
            if self.DBScanEngine == "MySQL":
                self.mysqlPostUpdateProcedure()
            os.remove(scanPIDFile)
            logger.info(">> INDEXING COMPLETED.")
            if isScanMode:
                logger.info("isScanMode - exit app")
                self.exitActionTriggered()

    def filterSearchInRemovedToggled(self):
        """When checkbox "Search in removed" is checked: unchecks "Indexed in last", renames "Indexed" column to "Removed" (and back)"""
        if self.FilterSearchInRemoved.isChecked():
            self.tableFiles.setHorizontalHeaderItem(self.tableFilesColumnIndexedIndx, QtWidgets.QTableWidgetItem("Removed"))
            self.FilterIndexedLastDaysEnabled.setText("Removed in last")
            self.btnSearch.setText("Search in removed...")
        else:
            self.tableFiles.setHorizontalHeaderItem(self.tableFilesColumnIndexedIndx, QtWidgets.QTableWidgetItem("Indexed "))
            self.FilterIndexedLastDaysEnabled.setText("Indexed in last")
            self.btnSearch.setText("Search...")

    def filterFilenameTextChanged(self):
        """Does not allow to run a search until the file name is specified."""
        if self.FilterFilename.text().strip() == "":
            self.btnSearch.setDisabled(True)
        else:
            self.btnSearch.setEnabled(True)

    def btnSearchEmitted(self):
        """Starts (or stops) the search process."""
        if self.btnSearch.text() == "Stop":
            try:
                self.SearchInDBThread.stop()
            except:
                pass
        elif self.btnSearch.text() == "Search..." or "Search in removed...":
            self.startSearching()
        elif self.btnSearch.text() == "Wait":
            pass
        else:
            pass

    def startSearching(self):
        """Cleans the results table, collects filters, runs the search threads depending on the database used."""

        # "self.btnSearch" will be enabled back by signal "self.SearchInDBThread.unlockSearchButton"
        # the idea is to block the button until the sql query is executed.
        self.btnSearch.setDisabled(True)
        self.btnSearch.setText("Wait")

        self.tableFiles.clearContents()
        self.tableFiles.setRowCount(0)
        self.checkingFileExistenceThreads = {}
        self.tableFilesFileIsChecked = {}  # see checkFilesExistence()
        self.tableFiles.setSortingEnabled(False)  # The list is updated in chunks. At the time of the process, I turned off the ability to sort  because of glitches.

        # Now we need to save elements 'isEnabled' states, block them, and restore states in searchInDBThreadSearchCompleteEmitted().
        # It's almost complete elements list, except "show all" checkbox, which must be active for searching interruption
        searchInterfaceElements = [
            "FilterSearchInRemoved",
            "FilterFilename",
            "FilterPath",
            "FilterFileTypes",
            "FilterListLineEdit",
            "FilterListRemoveButton",
            "FilterListComboBox",
            "FilterListSaveButton",
            "FilterIndexedLastDaysEnabled",
            "FilterIndexedLastDays",
            "FilterMinSizeEnabled",
            "FilterMinSize",
            "FilterMinSizeType",
            "FilterMaxSizeEnabled",
            "FilterMaxSize",
            "FilterMaxSizeType"
            ]
        self.searchInterfaceElementsStates = self.get_states_of_gui_elements(searchInterfaceElements)
        self.guiElementsSetDisabled(searchInterfaceElements)

        filters = {}
        filters["FilterSearchInRemoved"] = self.FilterSearchInRemoved.isChecked()
        filters["FilterFilename"] = self.FilterFilename.text()
        filters["FilterPath"] = self.FilterPath.text()
        filters["FilterFileTypes"] = self.FilterFileTypes.text()
        filters["FilterMixSizeEnabled"] = self.FilterMinSizeEnabled.isChecked()
        filters["FilterMinSizeType"] = self.FilterMinSizeType.currentText()
        filters["FilterMinSize"] = self.FilterMinSize.value()
        filters["FilterMaxSizeEnabled"] = self.FilterMaxSizeEnabled.isChecked()
        filters["FilterMaxSizeType"] = self.FilterMaxSizeType.currentText()
        filters["FilterMaxSize"] = self.FilterMaxSize.value()
        filters["FilterIndexedLastDaysEnabled"] = self.FilterIndexedLastDaysEnabled.isChecked()
        filters["FilterIndexedLastDays"] = self.FilterIndexedLastDays.value()
        filters["FilterShowMoreResultsEnabled"] = self.FilterShowMoreResultsCheckbox.isChecked()
        filters["FilterSearchLimit"] = self.settings.value("maxSearchResults")

        if self.settings.value("useExternalDatabase") == "False":
            self.SearchInDBThread = SearchInSqliteDB(self.DBCount.value(), filters)
        else:
            self.SearchInDBThread = SearchInMySQLDB(filters, self.settings)
        self.SearchInDBThread.rowEmitted.connect(self.searchInDBThreadRowEmitted)
        self.SearchInDBThread.unlockSearchButton.connect(self.enableStopButton)
        self.SearchInDBThread.searchComplete.connect(self.searchInDBThreadSearchCompleteEmitted)
        self.SearchInDBThread.start()
        self.SearchInDBThread.setPriority(QtCore.QThread.LowestPriority)

    def enableStopButton(self):
        """Makes the search button (as a stop button) active after completing the SQL query and starting to display search results."""
        self.btnSearch.setText("Stop")
        self.btnSearch.setEnabled(True)

    def searchInDBThreadRowEmitted(self, filename, path, size, ctime, mtime, indexed):
        """While executing sql - gets returned rows and inserts them into QTableWidget.
            Checks the option to limit the number of search results in the settings, if the number of results
            begins to exceed this number - makes visible the checkbox for disabling restrictions and stops the search thread.
            If the checkbox is set or the number of results does not exceed the limit from the settings - does not stop
            the search thread and displays all the results in the table"""
        row = self.tableFiles.rowCount()

        (ctime, mtime, indexed) = (str(datetime.datetime.fromtimestamp(ctime)),
                                   str(datetime.datetime.fromtimestamp(mtime)),
                                   str(datetime.datetime.fromtimestamp(indexed))
                                   )
        size = int(size)

        # limit
        if row > int(
                self.settings.value("maxSearchResults")) - 1 and not self.FilterShowMoreResultsCheckbox.isChecked():
            self.FilterShowMoreResultsCheckbox.setVisible(True)
            self.FilterShowMoreResultsCheckbox.setText("Show all results (can produce heavy load on DB and consume large amount of RAM on local PC.)")
            self.SearchInDBThread.stop()
            return

        self.tableFiles.insertRow(row)
        numItem = QtWidgets.QTableWidgetItem()
        numItem.setData(QtCore.Qt.EditRole, row + 1)
        self.tableFiles.setItem(row, self.tableFilesColumnNumIndx, numItem)
        self.tableFiles.setItem(row, self.tableFilesColumnFilnameIndx, QtWidgets.QTableWidgetItem(filename))
        self.tableFiles.setItem(row, self.tableFilesColumnTypeIndx, QtWidgets.QTableWidgetItem(
                                                utilities.get_extension_from_filename(filename)  # if there is a dot in filename - extract extension
                                                                                              )
                                )

        sizeItem = QtWidgets.QTableWidgetItem()
        # A python can work with large numbers even if it is 32-bit, but qt cannot insert
        # a large number into the table =((. So:
        if platform.architecture()[0] == "32bit" and size > 2147483646:
            size = float(size)
        sizeItem.setData(QtCore.Qt.EditRole, size)
        self.tableFiles.setItem(row, self.tableFilesColumnSizeIndx, sizeItem)
        self.tableFiles.setItem(row, self.tableFilesColumnModifiedIndx, QtWidgets.QTableWidgetItem(mtime))
        self.tableFiles.setItem(row, self.tableFilesColumnIndexedIndx, QtWidgets.QTableWidgetItem(indexed))
        self.tableFiles.setItem(row, self.tableFilesColumnCreatedIndx, QtWidgets.QTableWidgetItem(ctime))
        self.tableFiles.setItem(row, self.tableFilesColumnPathIndx, QtWidgets.QTableWidgetItem(path))

    def searchInDBThreadSearchCompleteEmitted(self):
        """After the search is completed, it unlocks the interface elements and forcibly launches the check for
            the existence of files visible to the user."""
        self.tableFiles.setSortingEnabled(True)
        self.guiElementsRestoreStates(self.searchInterfaceElementsStates)
        if self.FilterSearchInRemoved.isChecked():
            self.btnSearch.setText("Search in removed...")
        else:
            self.btnSearch.setText("Search...")
        self.checkFilesExistence() # This line activates the file existence check.

    def checkScanPIDFileLoopEmitted(self, fileExists):
        """Blocks the change in the number of internal databases during scanning into them"""
        if fileExists:
            self.DBCount.setDisabled(True)
            self.DBCountLabel.setText("DB Count (<font color=red>indexing...</font>): ")
            self.DBCountLabel.setToolTip("Check the pid file in the working directory if you are sure that indexing that indexing is stopped..")
            self.actionStartScan.setText("Indexing in progress")
            self.actionStartScan.setDisabled(True)
        else:
            self.DBCount.setEnabled(True)
            self.DBCountLabel.setText("DB Count: ")
            self.actionStartScan.setText("Start Indexing")
            self.actionStartScan.setEnabled(True)

    ## CHECKING FILE EXISTENCE
    #

    def tableFilesScrolled(self):
        """creates a countdown timer, or updates it.
        When the countdown expires, the signal starts checking the files.
       It was necessary for the smooth scrolling of search results when the check
       was not made into separate threads. At the moment, the delay simply allows you
       to avoid unnecessary checks with fast scrolling.."""
        delay = .5
        try:
            self.checkFileExistenceDelayer
            self.checkFileExistenceDelayer.currentTimer = delay
        except:
            self.checkFileExistenceDelayer = Delayer(delay)
            self.checkFileExistenceDelayer.sig.connect(self.checkFilesExistence)
            self.checkFileExistenceDelayer.sig.connect(self.removeCheckFileExistenceDelayer)
            self.checkFileExistenceDelayer.start()

    def removeCheckFileExistenceDelayer(self):
        """Removes the countdown timer (allows you to make a new one when tableFilesScrolled)"""
        self.checkFileExistenceDelayer.wait()
        self.checkFileExistenceDelayer = None
        del self.checkFileExistenceDelayer

    def checkFilesExistence(self, forcedCheck=False):
        """Defines the top and bottom visible row.
        For each row:
        if rowId (first column) is not in the dictionary
        - adds to the dictionary (it is cleaned with every new search)
        - start the thread of checking the file for existence.
        A thread emits a signal if the file is not found - the signal is associated with paintRowInRed()."""
        if self.tableFiles.rowCount() > 0:
            upRow = self.tableFiles.indexFromItem(self.tableFiles.itemAt(0, 0)).row()

            if self.tableFiles.itemAt(0, self.tableFiles.height()):
                downRow = self.tableFiles.indexFromItem(self.tableFiles.itemAt(0, self.tableFiles.height())).row()
            else:
                downRow = self.tableFiles.rowCount()

            for rowIndx in range(upRow, downRow):
                # In order not to check the full range of all rows, add the ID of checked
                # rows in dict self.tableFilesFileIsChecked. This dictionary is reset with a new search.
                rowId = self.tableFiles.item(rowIndx, self.tableFilesColumnNumIndx).text()
                if rowId not in self.tableFilesFileIsChecked or forcedCheck is True:
                    self.tableFilesFileIsChecked[rowId] = True
                    fullFilePath = self.tableFiles.item(rowIndx, self.tableFilesColumnPathIndx).text() + self.tableFiles.item(rowIndx, self.tableFilesColumnFilnameIndx).text()
                    if isWindows and not utilities.str2bool(self.settings.value("disableWindowsLongPathSupport")):
                        fullFilePath = "\\\\?\\" + fullFilePath
                    self.tableFilesFileIsChecked[rowId] = True

                    self.checkingFileExistenceThreads[rowIndx] = FileExistenceChecker(rowIndx, fullFilePath)
                    self.checkingFileExistenceThreads[rowIndx].rowSig.connect(self. paintRowInRed)
                    self.checkingFileExistenceThreads[rowIndx].start()

    def paintRowInRed(self, row):
        """Sets red background for row in search results"""
        for column in range(0, self.tableFiles.columnCount()):
            # setBackground instead of setBackgroundColor - for backward compatibility with pyside|qt4
            try:
                self.tableFiles.item(row, column).setBackground(QtGui.QColor(255, 161, 137))
            except:
                pass

    #
    ## CHECKING FILE EXISTENCE - END SECTION

    def guiElementsSetDisabled(self, elements):
        """Disable items on the list"""
        for element in elements:
            e = vars(self)[element]
            e.setDisabled(True)

    def guiElementsRestoreStates(self, elementsAndStates):
        """Apply enabled state saved with get_states_of_gui_elements()"""
        elements = elementsAndStates["elements"]
        states  = elementsAndStates["states"]

        for element in elements:
            e = vars(self)[element]
            e.setEnabled(states[element])

    def get_states_of_gui_elements(self, elements):
        """Returns elements and 'isEnabled' states"""
        elementsStates = {}
        for element in elements:
            e = vars(self)[element]
            elementsStates[element] = e.isEnabled()

        states = {"elements": elements, "states": elementsStates}
        return states

    def applyLoggingLevel(self):
        # set non-default logging level
        if self.settings.value("LogLevel") == "INFO":
            logger.setLevel(logging.INFO)
        elif self.settings.value("LogLevel") == "WARNINIG":
            logger.setLevel(logging.WARNING)
        elif self.settings.value("LogLevel") == "DEBUG":
            logger.setLevel(logging.DEBUG)

    def get_folder_size_and_files_count(self, dir):
        """Calculates and returns as a dictionary:
        the total size of the directory and subdirectories, and the total number of files"""
        if utilities.str2bool(self.settings.value("useExternalDatabase")) == True:
            # mysql part
            try:
                self.mysqlEstablishConnection()
            except:
                QtWidgets.QMessageBox.warning(self, __appname__, "Database connection error.")
                return

            cursor = self.dbConnMysql.cursor()
            query = """SELECT size FROM Files WHERE path LIKE %s AND removed > 0"""
            cursor.execute(query, (dir.replace('\\','\\\\') + "%",))
            sizes = cursor.fetchall()
            cursor.close()
            self.dbConnMysql.close()
        else:
            # sqlite part, about sql query logics read in "SearchInSqliteDB" class
            dbConn = sqlite3.connect(pathlib.Path(get_db_path(1)).as_uri() + "?mode=ro", uri=True)
            for i in range(2, self.DBCount.value() + 1):
                dbConn.execute("ATTACH DATABASE '" + get_db_path(i) + "' AS DB" + str(i))
            cursor = dbConn.cursor()
            parameters = []
            query = "SELECT  size FROM ("
            for i in range(1, self.DBCount.value() + 1):
                if i == 1:
                    query += " SELECT filename, path, size FROM Files f" + str(i) + " WHERE UPPER(path) GLOB UPPER(?) AND removed > 0"
                    parameters += [dir + "*"]
                else:
                    query += " UNION ALL SELECT filename, path, size FROM DB" + str(i) + ".Files f" + str(i) + " WHERE UPPER(path) GLOB UPPER(?) AND removed > 0"
                    parameters += [dir + "*"]
            query += ") T GROUP BY filename, path"
            cursor.execute(query, parameters)
            sizes = cursor.fetchall()
            cursor.close()
            dbConn.close()

        resultSize = 0
        filesCount = 0
        for size in sizes:
            resultSize += size[0]
            filesCount += 1

        result = {"size": resultSize, "filesCount": filesCount}
        return result

    def refreshSQLTabs(self):
        """Switches the availability of external and internal database tabs depending on settings"""
        if self.settings.value("useExternalDatabase") == "False":
            self.tabsSearch.setTabEnabled(1, True)
            self.tabsSearch.setTabEnabled(2, False)
        else:
            self.tabsSearch.setTabEnabled(1, False)
            self.tabsSearch.setTabEnabled(2, True)

    def loadPidChecker(self):
        """Starts thread with infinite checking pid file of indexing process"""
        self.mycheckScanPIDFileLoopThread = CheckScanPIDFileLoopThread()
        self.mycheckScanPIDFileLoopThread.pidFileExists.connect(self.checkScanPIDFileLoopEmitted)
        self.mycheckScanPIDFileLoopThread.start()

    def exitActionTriggered(self):
        """Exit the application"""
        self.close()

    def closeEvent(self, event, *args, **kwargs):
        """Overrides the default close method"""
        self.mycheckScanPIDFileLoopThread.stop()
        self.mycheckScanPIDFileLoopThread.wait()


# PID-FILE CHECKER
class CheckScanPIDFileLoopThread(QtCore.QThread):
    pidFileExists = QtCore.Signal(bool)
    _isRunning = True

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self)

    def run(self):
        self.pid_check()

    def pid_check(self):
        while self._isRunning is True:
            if os.path.isfile(scanPIDFile):
                self.pidFileExists.emit(True)
            else:
                self.pidFileExists.emit(False)
            time.sleep(1)

    def stop(self):
        self._isRunning = False


# DELAYER THREAD
class Delayer(QtCore.QThread):
    sig = QtCore.Signal(int)

    def __init__(self, timer=3, parent=None):
        QtCore.QThread.__init__(self)

        self.defaultTimer = timer
        self.currentTimer = timer

    def run(self):
        self.run_timer()

    def run_timer(self):
        while self.currentTimer > 0:
            time.sleep(.1)
            self.currentTimer -= .1
        self.sig.emit(0)


# CHECK FILE EXISTENCE THREAD
class FileExistenceChecker(QtCore.QThread):
    rowSig = QtCore.Signal(int)

    def __init__(self, row, fullPathToFile, parent=None):
        QtCore.QThread.__init__(self)

        self.row = row
        self.fullPathToFile = fullPathToFile

    def run(self):
        self.check_file()

    def check_file(self):
        logger.debug("Checking file: {}".format(self.fullPathToFile))
        try:
            if not os.path.isfile(self.fullPathToFile):
                logger.debug("... not found: {}".format(self.fullPathToFile))
                self.rowSig.emit(self.row)
            else:
                logger.debug("...   checked: {}".format(self.fullPathToFile))
        except Exception as e:
            logger.warning(str(e))
        logger.debug("Checking file: {} complete".format(self.fullPathToFile))


# HUMANIZATOR FOR SIZE COLUMN
class SizeItemDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self)

    def displayText(self, value, locale=None):
        return utilities.get_humanized_size(value)

    def createEditor(self, parent, option, index):
        """custom readonly QlineEdit"""
        lineEdit = QtWidgets.QLineEdit(parent)
        lineEdit.setReadOnly(True)
        return lineEdit


# SQLITE CLASSES
class UpdateSqliteDBThread(QtCore.QThread):
    sigIsOver = QtCore.Signal(int)

    def __init__(self, DBNumber, settings, parent=None):
        QtCore.QThread.__init__(self)

        self.settings = settings
        self.DBNumber = DBNumber

    def run(self):

        logger.info("Scan thread #" + str(self.DBNumber) + ". Started.")

        self.dbConn = sqlite3.connect(get_db_path(self.DBNumber))
        self.dbCursor = self.dbConn.cursor()

        exclusions = self.dbCursor.execute("SELECT value FROM Settings WHERE option=?",
                                           ("Exclusions",)).fetchone()[0]

        exclusionsMode = self.dbCursor.execute("SELECT value FROM Settings WHERE option=?",
                                               ("ExclusionsMode",)).fetchone()[0]

        rootPath = self.dbCursor.execute("SELECT value FROM Settings WHERE option=?", ("RootPath",)).fetchone()[0]

        if rootPath:
            logger.debug("Scan thread #" + str(self.DBNumber) + ". Path: " + rootPath)
            self.updateSqliteDB(str(rootPath), exclusions, exclusionsMode)

        self.sigIsOver.emit(self.DBNumber)

    def updateSqliteDB(self, rootpath, exclusions=None, exclusionsMode=None):
        """Scan filesystem from given path"""
        if isWindows and not utilities.str2bool(self.settings.value("disableWindowsLongPathSupport")):
            self.windowsLongPathHack = True
        else:
            self.windowsLongPathHack = False

        if self.windowsLongPathHack:
            rootpath = "\\\\?\\" + rootpath

        exclusions = exclusions.split(",")
        logger.debug("Scan thread #" + str(self.DBNumber) + ". Setting up removed flag for all files in DB...")
        self.dbCursor.execute("UPDATE Files SET removed=? WHERE removed <> ? ", ("0", "-1"))
        self.dbConn.commit()
        logger.debug("Scan thread #" + str(self.DBNumber) + ". Setting up removed flag. Complete.")

        timer = time.time()
        filesIndexed = 0
        filesCommited = 0

        for entry in utilities.scantree(rootpath):
            if entry.is_file():
                hash = md5()

                # commit every 3 sec
                if time.time() - timer > 4:
                    logger.debug("Scan thread #" + str(self.DBNumber) +  ". Committing to DB " + str(filesCommited) + " files.")
                    self.dbConn.commit()
                    logger.debug("Scan thread #" + str(self.DBNumber) + ". Committed.")
                    self.dbConn.close()
                    time.sleep(0.1)
                    logger.debug("Scan thread #" + str(self.DBNumber) + ". Open new connection to db")
                    self.dbConn = sqlite3.connect(get_db_path(self.DBNumber))
                    self.dbCursor = self.dbConn.cursor()
                    timer = time.time()
                    filesCommited = 0

                try:
                    name = entry.name

                    extension = utilities.get_extension_from_filename(name)

                    if (extension in exclusions and exclusionsMode == "Whitelist"
                    ) or (
                            extension not in exclusions and exclusionsMode == "Blacklist"
                    ) or (
                            len(exclusions) == 1 and exclusions[0] == ""
                    ):
                        fullname = entry.path  # full path + filename
                        path = fullname[:-len(name)]
                        if self.windowsLongPathHack:
                            path = path[4:]
                        size = int(entry.stat().st_size)
                        mtime = int(entry.stat().st_mtime)
                        ctime = int(entry.stat().st_ctime)
                        now = int(time.time())
                        hash.update(fullname.encode())
                        key = hash.hexdigest()

                        # SQL TABLE: hash, removed, filename, path, size, created, modified, indexed
                        data = self.dbCursor.execute("SELECT indexed, removed FROM Files WHERE hash=?", (key,)).fetchone()
                        if data is None: # new file
                            indexed = now
                        else:
                            if  data[1] == "-1": # file as removed in db, so refresh indexed time
                                indexed = now
                            else:
                                indexed = data[0]

                        self.dbCursor.execute("INSERT OR REPLACE INTO Files VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                              (key, "1", name, path, size, ctime, mtime, indexed))
                        filesIndexed += 1
                        filesCommited += 1
                except Exception as e:
                    logger.critical("Error while scan and update DB: " + str(e) + ". Stopping thread.")
                    self.sigIsOver.emit(self.DBNumber)
                    self.exit(1)

        logger.info("Scan thread #" + str(self.DBNumber) + ". Final commit. Files indexed (total in thread):" + str(filesIndexed))
        self.dbConn.commit()
        logger.debug("Scan thread #" + str(self.DBNumber) + ". Cleaninig.")

        currentTime = int(time.time())
        SaveRemovedFilesForDaysInSec = int(self.settings.value("SaveRemovedFilesForDays")) * 86400
        removedTime = currentTime - SaveRemovedFilesForDaysInSec
        if int(self.settings.value("SaveRemovedFilesForDays")) != 0:
            self.dbCursor.execute("UPDATE Files SET indexed=?, removed =?  WHERE removed=?", (currentTime, "-1", "0"))
            self.dbConn.commit()
            removedCounter = self.dbCursor.rowcount
            logger.info("Scan thread #" + str(self.DBNumber) + ". Files set as removed: " + str(removedCounter))
            self.dbCursor.execute("DELETE FROM Files WHERE removed = ? AND indexed < ?", ("-1", removedTime))
            self.dbConn.commit()
            cleanCounter = self.dbCursor.rowcount
            logger.info("Scan thread #" + str(self.DBNumber) + ". Files removed from db: " + str(cleanCounter))
        else:
            logger.debug("Scan thread #" + str(self.DBNumber) + ". SaveRemovedFilesForDays=0, all removed files will be removed from db")
            self.dbCursor.execute("DELETE FROM Files WHERE removed = ? OR  removed = ?", ("-1", "0"))
            self.dbConn.commit()
            cleanCounter = self.dbCursor.rowcount
            logger.info("Scan thread #" + str(self.DBNumber) + ". Files removed from db: " + str(cleanCounter))

        logger.debug("Scan thread #" + str(self.DBNumber) + ". Vacuum.")
        self.dbConn.execute("VACUUM")
        logger.debug("Scan thread #" + str(self.DBNumber) + ". Vacuum complete.")


class SearchInSqliteDB(QtCore.QThread):
    rowEmitted = QtCore.Signal(str, str, str, int, int, int)
    searchComplete = QtCore.Signal()
    unlockSearchButton = QtCore.Signal(bool)
    dbConn = {}
    _isRunning = True

    def __init__(self, DBCount, filters, parent=None):
        QtCore.QThread.__init__(self)

        self.DBCount = DBCount
        self.filters = filters

    def stop(self):
        self._isRunning = False

    def run(self):
        self.sqliteSearch()

    def sqliteSearch(self):
        """Execute SQL query, emits values"""

        # I connect to the first database and, if there are more, attach them as DB2, DB3, etc.
        self.dbConn = sqlite3.connect(pathlib.Path(get_db_path(1)).as_uri() + "?mode=ro", uri=True)
        for i in range(2, self.DBCount + 1):
            self.dbConn.execute("ATTACH DATABASE '" + get_db_path(i) + "' AS DB" + str(i))

        # I am forming a sql query. It looks a little scary, but in fact
        # the loop and the pieces before and after it forms such a string:
        # SELECT... FROM (SELECT ... FROM Files WHERE...) (UNION ALL SELECT ... FROM DB#.Files WHERE ...) ( GROUP BY ... LIMIT ...)
        # loops:                             ^first one                    ^second and others^        after loops^
        parameters = []
        query = "SELECT filename, path, size, created, modified, indexed FROM ("
        for i in range(1, self.DBCount + 1):
            dbCursor = self.dbConn.cursor()
            # SQL TABLE: hash, removed, filename, path, size, created, modified, indexed
            if i == 1:
                query += " SELECT filename, path, size, created, modified, indexed FROM Files f" + str(i) + " WHERE 1 "
            else:
                query += " UNION ALL SELECT filename, path, size, created, modified, indexed FROM DB" + str(i) + ".Files f" + str(i) + " WHERE 1 "

            # # query constructor
            # filename
            if self.filters["FilterFilename"].strip() != "":
                query += " AND (UPPER(filename) GLOB UPPER(?)) "
                parameters += ["" + self.filters["FilterFilename"] + ""]
            # path
            if self.filters["FilterPath"].strip() != "":
                query += " AND (UPPER(path) GLOB UPPER(?)) "
                parameters += ["*" + self.filters["FilterPath"] + "*"]
            # extensions
            if self.filters["FilterFileTypes"].strip() != "":
                query += " AND ("
                exts = list(set(self.filters["FilterFileTypes"].split(",")))  # uniqify exts filter
                for ext in exts:
                    query += " UPPER(filename) GLOB UPPER(?) "
                    parameters += ["*." + ext]
                    if exts.index(ext) < len(exts) - 1:
                        # print(str(exts.index(ext)) + " " + str(len(exts) - 1))
                        query += " OR"
                query += ")"
            # min size
            if self.filters["FilterMixSizeEnabled"]:
                if self.filters["FilterMinSizeType"] == "b":
                    minsize = self.filters["FilterMinSize"]
                if self.filters["FilterMinSizeType"] == "Kb":
                    minsize = self.filters["FilterMinSize"] * 1024
                if self.filters["FilterMinSizeType"] == "Mb":
                    minsize = self.filters["FilterMinSize"] * 1048576
                if self.filters["FilterMinSizeType"] == "Gb":
                    minsize = self.filters["FilterMinSize"] * 1073741824

                query += " AND (size >= ?)"
                parameters += [minsize]
            # max size
            if self.filters["FilterMaxSizeEnabled"]:
                if self.filters["FilterMaxSizeType"] == "b":
                    maxsize = self.filters["FilterMaxSize"]
                if self.filters["FilterMaxSizeType"] == "Kb":
                    maxsize = self.filters["FilterMaxSize"] * 1024
                if self.filters["FilterMaxSizeType"] == "Mb":
                    maxsize = self.filters["FilterMaxSize"] * 1048576
                if self.filters["FilterMaxSizeType"] == "Gb":
                    maxsize = self.filters["FilterMaxSize"] * 1073741824

                query += " AND (size <= ?)"
                parameters += [maxsize]
            # indexed in last days
            if self.filters["FilterIndexedLastDaysEnabled"]:
                filterInSeconds = self.filters["FilterIndexedLastDays"] * 86400
                queryTime = int(time.time()) - filterInSeconds
                query += " AND (Indexed > ?)"
                parameters += [queryTime]
            if self.filters["FilterSearchInRemoved"]:
                query += " AND (removed = ?) "
                parameters += ["-1"]
            else:
                query += " AND (removed <> ?) "
                parameters += ["-1"]
        # close first SELECT and remove duplicates by GROUP
        query += ") T GROUP BY filename, path  "
        # limit
        if not self.filters["FilterShowMoreResultsEnabled"]:
            # I request one result more than a certain limit in the settings. If there are really more results,
            # their number can be compared with the limit in the function responsible for filling in a QTableWidget
            # (searchInDBThreadRowEmitted), and showing the checkbox to disable the limit.
            limit = int(self.filters["FilterSearchLimit"]) + 1
            query += "LIMIT ?"
            parameters += [limit]
        query += ""  # for some cases )
        logger.debug("Execute search query with parameters: " + query + str(parameters))
        dbCursor.execute(query, parameters)
        self.unlockSearchButton.emit(True)
        for row in utilities.sql_search_result_iterator(dbCursor):
            if not self._isRunning:  # this variable can be changed from main class for search interruption
                self.searchComplete.emit()
                return
            filename, path, size, ctime, mtime, indexed = row[0], row[1], row[2], row[3], row[4], row[5]

            # next one is needed because Signal cannot (?) emmit integer over 4 bytes,
            # so doubleconverted - in this place and in searchInDBThreadRowEmitted()
            size = str(size)
            self.rowEmitted.emit(filename, path, size, ctime, mtime, indexed)
            time.sleep(.005)
        self.unlockSearchButton.emit(True)
        self.searchComplete.emit()


class SaveSqliteDBSettingsThread(QtCore.QThread):
    settingsSavedSig = QtCore.Signal(int)

    def __init__(self, DBNumber, dbSettings, parent=None):
        QtCore.QThread.__init__(self)

        self.DBNumber = DBNumber
        self.dbSettings = dbSettings

    def run(self):
        logger.info("Saving settings for DB #" + str(self.DBNumber))
        self.dbConn = sqlite3.connect(get_db_path(self.DBNumber))
        self.dbCursor = self.dbConn.cursor()

        self.save_setting_to_db("Exclusions", self.dbSettings["DBFileTypeFilter"])

        self.save_setting_to_db("ExclusionsMode", self.dbSettings["DBFileTypeFilterMode"])
        if self.dbSettings["DBRootScanPath"] != "[Path is not set]":
            self.save_setting_to_db("RootPath", self.dbSettings["DBRootScanPath"])
        self.dbConn.commit()
        self.dbConn.close()

        self.settingsSavedSig.emit(self.DBNumber)

    def save_setting_to_db(self, option, value):
        try:
            logger.debug("Save settings to sqlite: " + "UPDATE Settings SET value = ? WHERE option=?"  + str([value, option]))
            self.dbCursor.execute("UPDATE Settings SET value = ? WHERE option=?", (value, option))
        except Exception as e:
            logger.critical("Unable to write option to DB" + str(self.DBNumber) + "\r\n" +
                            "Error:\r\n" + str(e))
            if isScanMode == False:
                QtWidgets.QMessageBox.critical(self, __appname__,
                                               "Unable to write option to DB" + str(self.DBNumber) + "\r\n" +
                                               "Error:\r\n" + str(e))


# MySQL CLASSES
class SearchInMySQLDB(QtCore.QThread):
    rowEmitted = QtCore.Signal(str, str, str, int, int, int)
    searchComplete = QtCore.Signal()
    unlockSearchButton = QtCore.Signal(bool)
    dbConn = {}
    _isRunning = True

    def __init__(self, filters, settings, parent=None):
        QtCore.QThread.__init__(self)

        self.settings = settings
        self.filters = filters

    def stop(self):
        self._isRunning = False

    def run(self):
        self.mySQLSearch()

    def open_connection(self):
        try:
            self.dbConn = my_sql.connect(
                host=self.settings.value("MySQL/MySQLServerAddress"),
                port=int(self.settings.value("MySQL/MySQLServerPort")),
                user=self.settings.value("MySQL/MySQLLogin"),
                passwd=self.settings.value("MySQL/MySQLPassword"),
                db=self.settings.value("MySQL/MySQLDBName"),
                charset="utf8"
            )
        except Exception as e:
            logger.critical("Connection error: " + str(e))
            self.unlockSearchButton.emit(True)
            self.searchComplete.emit()
            raise Exception



    def mySQLSearch(self):
        """Execute SQL query, emits values"""

        try:
            self.open_connection()
        except:
            logger.warning("Searching interrupted")
            return

        dbCursor = self.dbConn.cursor()

        # SQL TABLE: hash, removed, filename, path, size, created, modified, indexed
        query = "SELECT filename, path, size, created, modified, indexed FROM Files WHERE 1 "
        parameters = []

        # # query constructor
        # filename
        if self.filters["FilterFilename"].strip() != "":
            query += " AND (filename LIKE %s) "
            parameters += ["" + utilities.mysql_query_wildficator(self.filters["FilterFilename"]) + ""]
        # path
        if self.filters["FilterPath"].strip() != "":
            query += " AND (path LIKE %s) "
            parameters += ["%" + utilities.mysql_query_wildficator(self.filters["FilterPath"].replace('\\','\\\\')) + "%"]
        # extensions
        extFromFileName = utilities.get_extension_from_filename(self.filters["FilterFilename"].strip())
        # If a file name with a simple extension (contains only letters, numbers, and _) is specified,
        # the extension will be extracted from the name and the extension filter will be ignored in any case.
        if re.match("[\w_]+$", extFromFileName):
            query += " AND (type = %s)"
            parameters += [extFromFileName]
        elif self.filters["FilterFileTypes"].strip() != "":
            query += " AND ("
            exts = list(set(self.filters["FilterFileTypes"].split(",")))  # uniqify exts filter
            for ext in exts:
                query += " type = %s "
                parameters += [ext]
                if exts.index(ext) < len(exts) - 1:
                    query += " OR"
            query += ")"
        else:
            pass
        # min size
        if self.filters["FilterMixSizeEnabled"]:
            if self.filters["FilterMinSizeType"] == "b":
                minsize = self.filters["FilterMinSize"]
            if self.filters["FilterMinSizeType"] == "Kb":
                minsize = self.filters["FilterMinSize"] * 1024
            if self.filters["FilterMinSizeType"] == "Mb":
                minsize = self.filters["FilterMinSize"] * 1048576
            if self.filters["FilterMinSizeType"] == "Gb":
                minsize = self.filters["FilterMinSize"] * 1073741824

            query += " AND (size >= %s)"
            parameters += [minsize]
        # max size
        if self.filters["FilterMaxSizeEnabled"]:
            if self.filters["FilterMaxSizeType"] == "b":
                maxsize = self.filters["FilterMaxSize"]
            if self.filters["FilterMaxSizeType"] == "Kb":
                maxsize = self.filters["FilterMaxSize"] * 1024
            if self.filters["FilterMaxSizeType"] == "Mb":
                maxsize = self.filters["FilterMaxSize"] * 1048576
            if self.filters["FilterMaxSizeType"] == "Gb":
                maxsize = self.filters["FilterMaxSize"] * 1073741824

            query += " AND (size <= %s)"
            parameters += [maxsize]
        # indexed in last days
        if self.filters["FilterIndexedLastDaysEnabled"]:
            filterInSeconds = self.filters["FilterIndexedLastDays"] * 86400
            queryTime = int(time.time()) - filterInSeconds
            query += " AND (Indexed > %s)"
            parameters += [queryTime]
        # in removed?
        if self.filters["FilterSearchInRemoved"]:
            query += " AND (removed = %s) "
            parameters += [-1]
        else:
            query += " AND (removed <> %s) "
            parameters += [-1]
        # limit
        if not self.filters["FilterShowMoreResultsEnabled"]:
            # I request one result more than a certain limit in the settings. If there are really more results,
            # their number can be compared with the limit in the function responsible for filling in a QTableWidget
            # (searchInDBThreadRowEmitted), and showing the checkbox to disable the limit.
            limit = int(self.filters["FilterSearchLimit"]) + 1
            query += "LIMIT %s"
            parameters += [limit]

        query += ""  # for some cases )
        logger.debug("Execute search query with parameters: " + query + str(parameters))
        dbCursor.execute(query, parameters)
        self.unlockSearchButton.emit(True)
        for row in utilities.sql_search_result_iterator(dbCursor):
            if not self._isRunning:  # this variable can be changed from main class for search process interruption
                self.searchComplete.emit()
                return
            filename, path, size, ctime, mtime, indexed = row[0], row[1], row[2], row[3], row[4], row[5]

            # next one is needed because Signal cannot (?) emmit integer over 4 bytes,
            # so doubleconverted - in this place and in searchInDBThreadRowEmitted()
            size = str(size)

            self.rowEmitted.emit(filename, path, size, ctime, mtime, indexed)
            time.sleep(.005)
        self.dbConn.close()
        self.unlockSearchButton.emit(True)
        self.searchComplete.emit()


class UpdateMysqlDBThread(QtCore.QThread):
    sigIsOver = QtCore.Signal(int)
    dbConn = None

    def __init__(self, path, threadID, removedKey, settings, parent=None):
        QtCore.QThread.__init__(self)

        self.settings = settings
        self.path = path
        self.threadID = threadID
        self.removedKey = int(removedKey)

    def run(self):
        logger.info("Scan thread #" + str(self.threadID) + ". Started. Path: " + self.path)
        try:
            self.open_connection()
        except:
            self.sigIsOver.emit(self.threadID)
            return

        self.updateMysqlDB(self.path, self.removedKey)
        self.sigIsOver.emit(self.threadID)

    def open_connection(self):

        try:
            self.dbConn = my_sql.connect(
                host=self.settings.value("MySQL/MySQLServerAddress"),
                port=int(self.settings.value("MySQL/MySQLServerPort")),
                user=self.settings.value("MySQL/MySQLLogin"),
                passwd=self.settings.value("MySQL/MySQLPassword"),
                db=self.settings.value("MySQL/MySQLDBName"),
                charset="utf8"
            )
        except Exception as e:
            logger.critical("Scan thread #" + str(self.threadID) + ". MySQL connection error: " + str(e))
            raise Exception


    def execute_and_commit_to_db(self, sql, values):
        '''commit files to DB'''
        dbCursor = self.dbConn.cursor()
        try:
            dbCursor.executemany(sql, values)
            self.dbConn.commit()
        except Exception as e:
            logger.critical("Scan thread #" + str(self.threadID) + ". MySQL execute and commit error: " + str(e) + ". Stopping thread.")
            raise Exception
        dbCursor.close()

    def updateMysqlDB(self, rootpath, removedKey):
        """Scan filesystem from given path"""
        if isWindows and not utilities.str2bool(self.settings.value("disableWindowsLongPathSupport")):
            self.windowsLongPathHack = True
        else:
            self.windowsLongPathHack = False

        if self.windowsLongPathHack:
            rootpath = "\\\\?\\" + rootpath

        filesIndexed = 0

        sqlTransactionLimit = int(self.settings.value("sqlTransactionLimit"))
        sqlTransactionCounter = 0
        varsArr = []
        # "indexed= IF... removed=..." order is important!!!!
        sql = """insert into `Files` (hash, removed, filename, type, path, size, created, modified, indexed)
              values(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE size=values(size), modified=values(modified), 
              indexed = IF(removed <> -1, indexed, values(indexed)), removed=values(removed) """

        for entry in utilities.scantree(rootpath):
            # commit to DB every N (sqlTransactionLimit) files
            if sqlTransactionCounter >= sqlTransactionLimit:
                logger.debug("Scan thread #" + str(self.threadID) + ", starting commit to MySQL. Files indexed: " + str(filesIndexed))
                try:
                    self.execute_and_commit_to_db(sql, varsArr)
                except:
                    return

                logger.debug("Scan thread #" + str(self.threadID) + ", comitted to MySQL. Files indexed: " + str(filesIndexed))
                sqlTransactionCounter = 0
                varsArr = []

            hash = md5()
            name = entry.name
            ext = utilities.get_extension_from_filename(name)
            fullname = entry.path  # full path + filename
            path = fullname[:-len(name)]
            if self.windowsLongPathHack:
                path = path[4:]
            size = int(entry.stat().st_size)
            mtime = int(entry.stat().st_mtime)
            ctime = int(entry.stat().st_ctime)
            indexed = int(time.time())
            hash.update(fullname.encode())
            key = str(hash.hexdigest())

            varsArr += [(key, removedKey, name, ext, path, size, ctime, mtime, indexed)]

            filesIndexed += 1
            sqlTransactionCounter += 1

        logger.debug("Scan thread #" + str(self.threadID) + ", starting FINAL commit to MySQL. Files indexed: " + str(filesIndexed))
        try:
            self.execute_and_commit_to_db(sql, varsArr)
        except:
            return
        logger.info("Scan thread #" + str(self.threadID) + " FINAL commit complete. Files indexed (total in thread):" + str(filesIndexed))


# DIALOG CLASSES
class AboutDialog(QtWidgets.QDialog, pyAbout.Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " - About")
        self.versionLabel.setText("(v. " + __version__ + ")")


class ShowLogDialog(QtWidgets.QDialog, pyLogViewer.Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " - LogFile:" + str(logfile))

        logtext = ""
        with open(logfile, 'r', encoding='utf-8-sig') as infile:
            for line in infile:
                logtext += line
        widgetText = "<pre>" +  str(logfile) + ":\n\r\n\r" + logtext + "</pre>"
        self.textEdit.setText(widgetText)

        # scroll to bottom
        self.textEdit.moveCursor(QtGui.QTextCursor.End)
        self.textEdit.moveCursor(QtGui.QTextCursor.StartOfLine)
        self.textEdit.ensureCursorVisible()


class HelpDialog(QtWidgets.QDialog, pyManual.Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " - Manual")


class PreferencesDialog(QtWidgets.QDialog, pyPreferences.Ui_Dialog):

    def __init__(self, initValues, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " - Preferences")

        self.PREFDisableWindowsLongPathSupport.setChecked(
            utilities.str2bool(initValues["disableWindowsLongPathSupport"]))
        self.PREFUseExternalDB.setChecked(utilities.str2bool(initValues["useExternalDatabase"]))
        self.PREFMaxSearchResults.setValue(int(initValues["maxSearchResults"]))
        self.PREFSaveRemovedInfoDays.setValue(int(initValues["SaveRemovedFilesForDays"]))
        self.PREFsqlTransactionLimit.setValue(int(initValues["sqlTransactionLimit"]))

        indx = self.PREFLoggingLevel.findText(initValues["LogLevel"])
        self.PREFLoggingLevel.setCurrentIndex(indx)

class FolderSizeDialog(QtWidgets.QDialog, pyFolderSize.Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " - Folder size")

        self.buttonGetSize.setDisabled(True)
        self.browseButton.clicked.connect(self.browseClicked)
        self.linePath.textEdited.connect(self.linePathEdited)
        self.buttonGetSize.clicked.connect(self.getSizeClicked)

    def browseClicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory", ".")
        if path:
            path = QtCore.QDir.toNativeSeparators(path)
            self.linePath.setText(path)
            self.linePathEdited()

    def linePathEdited(self):
        if len(self.linePath.text().strip()) > 0:
            self.buttonGetSize.setDisabled(False)
        else:
            self.buttonGetSize.setDisabled(True)

    def getSizeClicked(self):
        self.accept()

def unhandled_exception(exc_type, exc_value, exc_traceback):
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)

def get_db_path(DBNumber: int):
    return os.path.join(appDataPath,"DB" + str(DBNumber) + ".sqlite3")

def main():
    sys.excepthook = unhandled_exception

    if isScanMode and os.path.isfile(scanPIDFile):
        logger.warning("Scan is running already, check PID file. App closed.")
        sys.exit(0)

    QtCore.QCoreApplication.setApplicationName(__appname__)
    QtCore.QCoreApplication.setApplicationVersion(str(__version__))

    app = QtWidgets.QApplication(sys.argv)
    form = Main()
    if not isScanMode:
        form.show()

    app.exec_()


if __name__ == "__main__":
    main()
