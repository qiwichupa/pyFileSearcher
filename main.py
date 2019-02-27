# If you want to use it with python <3.6 and PySide:
# - replace "QtWidgets." with "QtGui."
# - replace "PySide2" with "PySide"
# - remove "import PySide2.QtWidgets as QtWidgets"
# - in utilities.py replace "from os import scandir" with "from scandir import scandir" (and install scandir module)
# - resave UI files and resources with Qt Designer and pyside utils

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets
import send2trash

# About this one.
# With python 3.7 and PySide2 and mysql.connector - I have memory leak in scan thread.
# So i prefer MySQLdb - it's fully compatible.
# But with python 3.4 and PySide - for win 2003 server build -  mysql.connector works fine,
# and MySQLdb is difficult to install. So I leave both of it here.
import MySQLdb as my_sql
#import mysql.connector as my_sql


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


__appname__ = "pyFileSearcher"
__version__ = "0.99e"

appDataPath = os.getcwd() + "/"
scanPIDFile = appDataPath + "scan.pid"
logfile = appDataPath + "pyfilesearcher.log"

logging.basicConfig(filename=logfile,
                    format="%(asctime)-15s: %(name)-18s - %(levelname)-8s - %(module)-15s - %(funcName)-20s - %(lineno)-6d %(message)s",
                    level=logging.DEBUG)
logger = logging.getLogger(name="main-gui")
sys.stdout = utilities.LoggerWriter(logger.warning)
sys.stderr = utilities.LoggerWriter(logger.warning)


if len(sys.argv) <= 1 or sys.argv[1] != "--scan":
    isScanMode = False
else:
    isScanMode = True

if platform.system() == "Linux":
    isLinux = True
    isWindows = False
elif platform.system() == "Windows":
    isWindows = True
    isLinux = False
else:
    sys.exit("This app is for only Linux and Windows, sorry!")


def get_db_path(DBNumber: int):
    return (appDataPath + "DB" + str(DBNumber) + ".sqlite3")


class Main(QtWidgets.QMainWindow, pyMain.Ui_MainWindow):
    sigUpdateDB = QtCore.Signal(str)
    dbConn = {}

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

        self.settings = QtCore.QSettings(appDataPath + "settings.ini", QtCore.QSettings.IniFormat)

        # Menu items
        self.actionPreferences.triggered.connect(self.actionPreferencesEmitted)
        self.actionStartScan.triggered.connect(self.updateDBEmitted)
        self.actionAbout.triggered.connect(self.actionAboutEmitted)
        self.actionShowHelpInfo.triggered.connect(self.actionShowHelpInfoEmitted)
        self.actionExit.triggered.connect(self.exitActionTriggered)
        self.actionOpenLog.triggered.connect(self.actionOpenLogEmitted)

        # Search Tab
        FilterFilenameValidator = QtGui.QRegExpValidator(QtCore.QRegExp("([\w \.\*\?-])*"), self)
        self.FilterFilename.setValidator(FilterFilenameValidator)
        self.FilterFilename.textEdited.connect(self.FilterFilenameTextChanged)
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
        self.tableFiles.contextMenuEvent = self.tableMenu

        self.tableFiles.itemEntered.connect(self.tableFilesScrolled)
        self.tableFiles.cellClicked.connect(self.tableFilesScrolled)

        # Search Tab - Filter List
        FilterListLineEditalidator = QtGui.QRegExpValidator(QtCore.QRegExp("([a-z0-9_-])*"), self)
        self.FilterListLineEdit.setValidator(FilterListLineEditalidator)

        self.FilterListSaveButton.setDisabled(True)

        self.FilterListLineEdit.textEdited.connect(self.FilterListLineEditEditedEmitted)

        self.FilterListSaveButton.clicked.connect(self.FilterListSaveButtonEmitted)
        self.FilterListRemoveButton.clicked.connect(self.FilterListRemoveButtonEmitted)
        self.FilterListComboBox.activated.connect(self.FilterListComboBoxEmitted)

        # Database Tab
        DBFileTypeFilterValidator = QtGui.QRegExpValidator(QtCore.QRegExp("(^[,])?([a-z0-9]{1,8},)*"), self)
        self.DBFileTypeFilter.setValidator(DBFileTypeFilterValidator)

        self.DBSelectDatabase.activated.connect(self.select_db)
        self.DBCount.valueChanged.connect(self.dbCountEmitted)

        self.DBFileTypeFilter.textEdited.connect(self.DBFileTypeFilterEmitted)
        self.DBFileTypeFilterMode.activated.connect(self.DBFileTypeFilterModeEmitted)
        self.DBRootScanPath.activated.connect(self.DBRootScanPathEmitted)

        self.DBApplySettingsButton.setDisabled(True)
        self.DBApplySettingsButton.clicked.connect(self.DBApplySettingsButtonEmitted)

        # MySQL tab
        self.MySQLServerAddress.textEdited.connect(self.MySQLServerAddressEmitted)
        self.MySQLServerPort.textEdited.connect(self.MySQLServerPortEmitted)
        self.MySQLDBName.textEdited.connect(self.MySQLDBNameEmitted)
        self.MySQLLogin.textEdited.connect(self.MySQLLoginEmitted)
        self.MySQLPassword.textEdited.connect(self.MySQLPasswordEmitted)

        self.MySQLTestButton.clicked.connect(self.MySQLTestButtonEmitted)
        self.MySQLInitDBCheckBox.toggled.connect(self.MySQLInitDBButton.setEnabled)
        self.MySQLInitDBButton.clicked.connect(self.MySQLInitDBButtonEmitted)

        self.MySQLPathsTableAddButton.clicked.connect(self.MySQLPathsTableAddButtonEmitted)
        self.MySQLPathsTableRemoveButton.clicked.connect(self.MySQLPathsTableRemoveButtonEmitted)

        self.MySQLPathsTable.itemSelectionChanged.connect(self.MySQLPathsTableItemSelectionChanged)

        # Load Settings
        self.load_initial_settings()

        # Checking pid file of indexing process for locking some parts of interface
        self.load_pid_checker()

        # run scan with --scan parameter
        if isScanMode:
            logger.info("Scan is running with command promt parameter!")
            self.updateDBEmitted()

    def load_initial_settings(self):
        """Load initial settings from configuration file and database"""

        if not self.settings.value("LogLevel"):
            self.settings.setValue("LogLevel", "INFO")
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

        #set non-default logging level
        if self.settings.value("LogLevel") == "INFO":
            logger.setLevel(logging.INFO)
        elif self.settings.value("LogLevel") == "WARNINIG":
            logger.setLevel(logging.WARNING)
        elif self.settings.value("LogLevel") == "DEBUG":
            logger.setLevel(logging.DEBUG)

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
                self.create_db(DBNumber)

            if self.select_db(DBNumber, False):
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

        self.MySQLPathsTableItemSelectionChanged()


# MAIN MENU ACTIONS
#
    def actionPreferencesEmitted(self):
        """Opens the preferences dialog"""
        initValues = {"useExternalDatabase": self.settings.value("useExternalDatabase"),
                      "disableWindowsLongPathSupport": self.settings.value("disableWindowsLongPathSupport"),
                      "maxSearchResults": self.settings.value("maxSearchResults"),
                      "LogLevel": self.settings.value("LogLevel")
                      }
        dialog = PreferencesDialog(initValues)
        if dialog.exec_():
            self.settings.setValue("useExternalDatabase", utilities.bool2str(dialog.PREFUseExternalDB.isChecked()))
            self.settings.setValue("disableWindowsLongPathSupport",
                                   utilities.bool2str(dialog.PREFDisableWindowsLongPathSupport.isChecked()))
            self.settings.setValue("maxSearchResults", str(dialog.PREFMaxSearchResults.value()))
            self.settings.setValue("LogLevel", dialog.PREFLoggingLevel.currentText())

            self.refreshSQLTabs()

    def updateDBEmitted(self):
        """Starts the file system scan. Depending on the settings, it generates scanning threads of either
            an internal or external database. For each thread, an updateDBThreads element is created, which is
            subsequently deleted to determine the end of the scan."""
        logger.info("UPDATING DB WAS STARTED. Creating PID-file: " + scanPIDFile)
        os.close(os.open(scanPIDFile, os.O_CREAT))

        self.updateDBThreads = {}

        if self.settings.value("useExternalDatabase") == "False":
            self.DBScanEngine = "Sqlite"
            for DBNumber in range(1, self.DBCount.value() + 1):
                self.updateDBThreads[DBNumber] = UpdateDBThread(DBNumber, self.settings)
                self.updateDBThreads[DBNumber].sigIsOver.connect(self.removeScanThreadWhenThreadIsOver)
                self.updateDBThreads[DBNumber].start()
        else:
            self.DBScanEngine = "MySQL"
            self.mysql_prepare_db_for_update()
            for row in range(0, self.MySQLPathsTable.rowCount()):
                path = self.MySQLPathsTable.item(row, 0).text()
                self.updateDBThreads[row] = UpdateMysqlDBThread(path, row, self.newRemovedKey, self.settings)
                self.updateDBThreads[row].sigIsOver.connect(self.removeScanThreadWhenThreadIsOver)
                self.updateDBThreads[row].start()

    def actionAboutEmitted(self):
        """Shows about dialog"""
        dialog = AboutDialog()
        dialog.pushButton.clicked.connect(dialog.close)
        dialog.exec_()

    def actionShowHelpInfoEmitted(self):
        """Shows help dialog"""
        dialog = HelpDialog()
        dialog.pushButton.clicked.connect(dialog.close)
        dialog.exec_()

    def actionOpenLogEmitted(self):
        """Shows log-file content"""
        dialog = OpenLogDialog()
        dialog.exec_()

#
# MAIN MENU ACTIONS - END SECTION

# SAVE/LOAD FILTERS
#
    def FilterListSaveButtonEmitted(self):
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
        self.settings.setValue("FILTER_" + filterName + "/FilterIndexedLastDaysEnabled",
                               self.FilterIndexedLastDaysEnabled.isChecked())

        self.settings.setValue("filters", ",".join(self.filters))

        self.FilterListLineEdit.setText("")

        # setCurrentIndex instead of setCurrentText - for backward compatibility with pyside|qt4
        listIndex = self.FilterListComboBox.findText(filterName)
        self.FilterListComboBox.setCurrentIndex(listIndex)

    def FilterListComboBoxEmitted(self):
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

        self.FilterFilenameTextChanged()

        self.FilterListLineEdit.setText(filterName)
        self.FilterListSaveButton.setEnabled(True)
        self.FilterListRemoveButton.setEnabled(True)

    def FilterListLineEditEditedEmitted(self):
        """Disables the save preset button if the preset name is not specified."""
        if self.FilterListLineEdit.text() == "":
            self.FilterListSaveButton.setDisabled(True)
        else:
            self.FilterListSaveButton.setEnabled(True)

    def FilterListRemoveButtonEmitted(self):
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
    def MySQLServerAddressEmitted(self):
        """Saves MySQL server address to settings"""
        self.settings.setValue("MySQL/MySQLServerAddress", self.MySQLServerAddress.text())
        pass

    def MySQLServerPortEmitted(self):
        """Saves MySQL server port to settings"""
        self.settings.setValue("MySQL/MySQLServerPort", self.MySQLServerPort.text())
        pass

    def MySQLDBNameEmitted(self):
        """Saves MySQL database name to settings"""
        self.settings.setValue("MySQL/MySQLDBName", self.MySQLDBName.text())
        pass

    def MySQLLoginEmitted(self):
        """Saves MySQL login to settings"""
        self.settings.setValue("MySQL/MySQLLogin", self.MySQLLogin.text())
        pass

    def MySQLPasswordEmitted(self):
        """Saves MySQL password to settings"""
        self.settings.setValue("MySQL/MySQLPassword", self.MySQLPassword.text())
        pass

    def MySQLTestButtonEmitted(self):
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

    def MySQLInitDBButtonEmitted(self):
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

    def MySQLPathsTableAddButtonEmitted(self):
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

    def MySQLPathsTableRemoveButtonEmitted(self):
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

    def MySQLPathsTableItemSelectionChanged(self):
        """Checks for the presence of selected lines in the directory list.
           If something is selected, the delete button becomes active."""
        if self.MySQLPathsTable.selectedItems():
            self.MySQLPathsTableRemoveButton.setEnabled(True)
        else:
            self.MySQLPathsTableRemoveButton.setDisabled(True)

    def mysql_establish_connection(self):
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
            sys.exit(1)



    def mysql_prepare_db_for_update(self):
        """If there is - selects the first value of the column 'removed' and generates a random new one
            that does not coincide with it. When scanning, this value is set for all new or updated rows in the
            database to identify deleted files and delete them in mysql_post_update_procedure."""
        self.mysql_establish_connection()

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
            r = list(range(0, int(oldRemovedKey))) + list(range(int(oldRemovedKey)+1, 100))


        self.newRemovedKey = random.choice(r)
        logger.debug("...new removed key is: " + str(self.newRemovedKey) + "...")


        self.dbConnMysql.close()
        logger.info("MySQL preparation complete!")


    def mysql_post_update_procedure(self):
        """Deletes all rows whose column 'removed' value is different from the one selected in the mysql_prepare_db_for_update."""
        self.mysql_establish_connection()

        cursor = self.dbConnMysql.cursor()
        logger.info("MySQL post-update procedure...")
        logger.info("...removing deleted files from DB...")
        try:
            cursor.execute("DELETE FROM Files WHERE removed <> %s", (self.newRemovedKey,))
            self.dbConnMysql.commit()
        except Exception as e:
            logger.warning("...Cleaning DB error: " + str(e))

        self.dbConnMysql.close()
        logger.info("MySQL post-update procedure complete.")

#
# MySQL THINGS - END SECTION

# Sqlite THINGS
#
    def select_db(self, DBNumber, runViaGUI=True):
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

        return (True)

    def create_db(self, DBNumber):
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

    def remove_db(self, DBNumber):
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
                self.create_db(i)
                if self.select_db(i, False):
                    self.DBSelectDatabase.addItem("DB" + str(i))
                    self.DBSelectDatabase.setCurrentIndex(i - 1)
        elif newDBCount < oldDBCount:
            for i in range(oldDBCount, newDBCount, -1):
                dbForRemove = i
                self.remove_db(dbForRemove)
                if self.DBSelectDatabase.currentIndex() is dbForRemove - 1:
                    self.select_db(self.DBSelectDatabase.currentIndex() - 1)
                self.DBSelectDatabase.removeItem(dbForRemove - 1)
        else:
            pass
        self.settings.setValue("DBCount", newDBCount)

    def DBFileTypeFilterEmitted(self):
        """Sets Apply button active when Exclusions was edited"""
        self.DBApplySettingsButton.setEnabled(True)

    def DBFileTypeFilterModeEmitted(self):
        """Makes Apply button active when ExclusionsMode (Whitelist|Blacklist) was selected"""
        self.DBApplySettingsButton.setEnabled(True)

    def DBRootScanPathEmitted(self):
        """Makes Apply button active when path was selected, and sets path into first slot in combobox"""
        if self.DBRootScanPath.currentIndex() is 1:
            currentPath = self.DBRootScanPath.itemText(0)
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", currentPath)
            if path:
                path = QtCore.QDir.toNativeSeparators(path)
                self.DBRootScanPath.setItemText(0, path)
                self.DBApplySettingsButton.setEnabled(True)
            self.DBRootScanPath.setCurrentIndex(0)

    def DBApplySettingsButtonEmitted(self):
        """Saves internal database settings to it"""
        self.DBSelectDatabase.setDisabled(True)
        currentDB = self.DBSelectDatabase.currentIndex() + 1
        dbSettings = {}
        dbSettings["DBFileTypeFilter"] = self.DBFileTypeFilter.text()
        dbSettings["DBFileTypeFilterMode"] = self.DBFileTypeFilterMode.currentText()
        dbSettings["DBRootScanPath"] = self.DBRootScanPath.itemText(0)

        self.SaveSqliteDBSettingsThread = SaveSqliteDBSettingsThread(currentDB, dbSettings)
        self.SaveSqliteDBSettingsThread.settingsSavedSig.connect(self.SaveSqliteDBSettingsThreadSavedSigEmitted)
        self.SaveSqliteDBSettingsThread.start()

    def SaveSqliteDBSettingsThreadSavedSigEmitted(self, DBNumber):
        """After saving the settings - rereads the settings of the internal database and unlocks the interface"""
        self.select_db(DBNumber, False)
        self.DBSelectDatabase.setEnabled(True)
        self.DBApplySettingsButton.setDisabled(True)
        self.DBSelectDatabase.setFocus()

#
# Sqlite THINGS - END SECTION

# TABLE CONTEXT MENU
#
    def tableMenu(self, event):
        """Create context menu for tableFiles widget"""
        self.menu = QtWidgets.QMenu(self)

        menuOpenFolder = QtWidgets.QAction('Open Folder', self)
        menuOpenFolder.triggered.connect(self.menuOpenFolder)
        self.menu.addAction(menuOpenFolder)
        if len(self.tableFiles.selectedItems()) > 8 or len(self.tableFiles.selectedItems()) == 0:
            menuOpenFolder.setDisabled(True)

        menuDeleteFiles = QtWidgets.QAction('Move file(s) to Trash', self)
        menuDeleteFiles.triggered.connect(self.menuDeleteFiles)
        # menuDeleteFiles.setDisabled(True)
        self.menu.addAction(menuDeleteFiles)
        if len(self.tableFiles.selectedItems()) == 0:
            menuDeleteFiles.setDisabled(True)

        menuExportSelectedToCsv = QtWidgets.QAction('Export selected to CSV...', self)
        menuExportSelectedToCsv.triggered.connect(self.menuExportSelectedToCsv)
        self.menu.addAction(menuExportSelectedToCsv)
        if len(self.tableFiles.selectedItems()) == 0:
            menuExportSelectedToCsv.setDisabled(True)

        menuExportAllToCsv = QtWidgets.QAction('Export all to CSV...', self)
        menuExportAllToCsv.triggered.connect(self.menuExportAllToCsv)
        self.menu.addAction(menuExportAllToCsv)
        if self.tableFiles.rowCount() == 0:
            menuExportAllToCsv.setDisabled(True)

        self.menu.popup(QtGui.QCursor.pos())



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
                    QtWidgets.QMessageBox.warning(self, __appname__,  "Opening directory error: " + str(e))



    def menuDeleteFiles(self):
        """Delete selected files"""
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
        self.tableFilesScrolled()

    def menuExportSelectedToCsv(self):
        """Exports selected rows to csv"""
        csvObj = QtWidgets.QFileDialog.getSaveFileName(parent=None, caption=__appname__ + " - Save as csv",
                                                       directory=".", filter="Simple spreadsheet (*.csv)")
        if csvObj:
            rows = utilities.get_selected_rows_from_qtablewidget(self.tableFiles)
            try:
                with open(csvObj[0], 'w', newline='') as csvfile:
                    csvWriter = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)

                    for row in rows:
                        textRow = []
                        for item in row:
                            textRow += [item.text()]
                        csvWriter.writerow(textRow)
            except Exception as e:
                logger.warning("Error while exporting csv: " + str(e))
                QtWidgets.QMessageBox.warning(self, __appname__, "Error while exporting csv: " + str(e))

    def menuExportAllToCsv(self):
        """Exports all search results to csv"""
        self.tableFiles.selectAll()
        self.menuExportSelectedToCsv()

#
# TABLE CONTEXT MENU - END SECTION

    def removeScanThreadWhenThreadIsOver(self, ThreadNumber):
        """Catching signals of scanning threads. Removes a thread from the list of threads;
        if the list is empty, it starts the cleaning for MySQL and deletes the pid-file."""
        self.updateDBThreads[ThreadNumber].wait()
        del self.updateDBThreads[ThreadNumber]
        logger.info("Scan thread #" + str(ThreadNumber) + " is over.")
        if len(self.updateDBThreads) == 0:
            if self.DBScanEngine == "MySQL":
                self.mysql_post_update_procedure()
            os.remove(scanPIDFile)
            logger.info("Scan is complete!")
            if isScanMode:
                logger.info("isScanMode - exit app")
                self.exitActionTriggered()


    def FilterFilenameTextChanged(self):
        """Does not allow to run a search until the file name is specified."""
        if self.FilterFilename.text().strip() == "":
            self.btnSearch.setDisabled(True)
        else:
            self.btnSearch.setEnabled(True)

    def btnSearchEmitted(self):
        """Starts the search process. Cleans the results table,
            collects filters, runs the search threads depending on the database used."""
        self.tableFiles.clearContents()
        self.tableFiles.setRowCount(0)
        self.tableFilesFileIsChecked = {}  # see tableFilesScrolled()
        self.tableFiles.setSortingEnabled(False) # The list is updated in chunks. At the time of the process, I turned off the ability to sort  because of glitches.

        # avoid double "press" via pressing enter in filter EditLines
        if not self.btnSearch.isEnabled():
            return

        self.btnSearch.setDisabled(True)

        self.btnSearch.setText("Searching...")

        time.sleep(.2) # I think this helps the search button not to look "half-blocked"

        filters = {}
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
            self.SearchInSqliteDBThread = SearchInSqliteDB(self.DBCount.value(), filters)
            self.SearchInSqliteDBThread.rowEmitted.connect(self.SearchInDBThreadRowEmitted)
            self.SearchInSqliteDBThread.searchComplete.connect(self.SearchInDBThreadSearchCompleteEmitted)
            self.SearchInSqliteDBThread.start()
            self.SearchInSqliteDBThread.setPriority(QtCore.QThread.LowestPriority)
        else:

            self.SearchInSqliteDBThread = SearchInMySQLDB(filters, self.settings)
            self.SearchInSqliteDBThread.rowEmitted.connect(self.SearchInDBThreadRowEmitted)
            self.SearchInSqliteDBThread.searchComplete.connect(self.SearchInDBThreadSearchCompleteEmitted)
            self.SearchInSqliteDBThread.start()
            self.SearchInSqliteDBThread.setPriority(QtCore.QThread.LowestPriority)

    def SearchInDBThreadRowEmitted(self, filename, path, size, ctime, mtime, indexed):
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
            self.FilterShowMoreResultsCheckbox.setText("Show all results (NOT recommended! Uncheck during searching to stop loading the results)")
            self.FilterShowMoreResultsCheckbox.setToolTip("Can produce heavy load on database and consume large amount of memory on local PC.")
            self.SearchInSqliteDBThread.stop()
            return

        self.tableFiles.insertRow(row)
        numItem = QtWidgets.QTableWidgetItem()
        numItem.setData(QtCore.Qt.EditRole, row + 1)
        self.tableFiles.setItem(row, self.tableFilesColumnNumIndx, numItem)
        self.tableFiles.setItem(row, self.tableFilesColumnFilnameIndx, QtWidgets.QTableWidgetItem(filename))
        self.tableFiles.setItem(row, self.tableFilesColumnTypeIndx, QtWidgets.QTableWidgetItem(
                                                                    utilities.get_extension_from_filename(filename))
                                # if there is a dot in filename - extract extension
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

    def SearchInDBThreadSearchCompleteEmitted(self):
        """After the search is completed, it unlocks the interface elements and forcibly launches the check for
            the existence of files visible to the user."""
        self.tableFiles.setSortingEnabled(True)
        self.btnSearch.setDisabled(False)
        self.btnSearch.setText("Search...")
        self.tableFilesScrolled()

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

    def tableFilesScrolled(self):
        """Checks the top and bottom line in the file table, checks for the presence of files at the moment. Marks missing files with color."""
        if self.tableFiles.rowCount() == 0:
            return

        upRow = self.tableFiles.indexFromItem(self.tableFiles.itemAt(0, 0)).row()
        if self.tableFiles.itemAt(0, self.tableFiles.height()):
            downRow = self.tableFiles.indexFromItem(self.tableFiles.itemAt(0, self.tableFiles.height())).row()
        else:
            downRow = self.tableFiles.rowCount()

        for i in range(upRow, downRow):
            # In order not to check the full range of all rows, add the ID of checked
            # rows in dict self.tableFilesFileIsChecked. This dictionary is reset with a new search.
            rowId = self.tableFiles.item(i, self.tableFilesColumnNumIndx).text()
            if rowId not in self.tableFilesFileIsChecked:
                fullFilePath = self.tableFiles.item(i, self.tableFilesColumnPathIndx).text() + self.tableFiles.item(i, self.tableFilesColumnFilnameIndx).text()
                if isWindows and not utilities.str2bool(self.settings.value("disableWindowsLongPathSupport")):
                    fullFilePath = "\\\\?\\" + fullFilePath
                self.tableFilesFileIsChecked[rowId] = True
                if not os.path.isfile(fullFilePath):
                    for column in range(0, self.tableFiles.columnCount()):
                        # setBackground instead of setBackgroundColor - for backward compatibility with pyside|qt4
                        self.tableFiles.item(i, column).setBackground(QtGui.QColor(255, 161, 137))

    def refreshSQLTabs(self):
        """Switches the availability of external and internal database tabs depending on settings"""
        if self.settings.value("useExternalDatabase") == "False":
            self.tabsSearch.setTabEnabled(1, True)
            self.tabsSearch.setTabEnabled(2, False)
        else:
            self.tabsSearch.setTabEnabled(1, False)
            self.tabsSearch.setTabEnabled(2, True)

    def load_pid_checker(self):
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


# SQLITE CLASSES
class UpdateDBThread(QtCore.QThread):
    sigIsOver = QtCore.Signal(int)

    def __init__(self, DBNumber, settings, parent=None):
        QtCore.QThread.__init__(self)

        self.settings = settings
        self.DBNumber = DBNumber

    def run(self):

        logger.info("Scan thread is started for Sqlite DB #" + str(self.DBNumber))

        self.dbConn = sqlite3.connect(get_db_path(self.DBNumber))
        self.dbCursor = self.dbConn.cursor()

        exclusions = self.dbCursor.execute("SELECT value FROM Settings WHERE option=?",
                                           ("Exclusions",)).fetchone()[0]

        exclusionsMode = self.dbCursor.execute("SELECT value FROM Settings WHERE option=?",
                                               ("ExclusionsMode",)).fetchone()[0]

        rootPath = self.dbCursor.execute("SELECT value FROM Settings WHERE option=?", ("RootPath",)).fetchone()[0]
        if rootPath:
            self.updateDB(str(rootPath), exclusions, exclusionsMode)

        self.sigIsOver.emit(self.DBNumber)

    def updateDB(self, rootpath, exclusions=None, exclusionsMode=None):
        """Scan filesystem from given path"""
        if isWindows and not utilities.str2bool(self.settings.value("disableWindowsLongPathSupport")):
            self.windowsLongPathHack = True
        else:
            self.windowsLongPathHack = False

        if self.windowsLongPathHack:
            rootpath = "\\\\?\\" + rootpath

        exclusions = exclusions.split(",")

        self.dbCursor.execute("UPDATE Files SET removed=?", ("0",))

        timer = time.time()

        for entry in utilities.scantree(rootpath):
            if entry.is_file():
                hash = md5()

                # commit every 3 sec
                if time.time() - timer > 4:
                    self.dbConn.commit()
                    self.dbConn.close()
                    time.sleep(0.1)
                    self.dbConn = sqlite3.connect(get_db_path(self.DBNumber))
                    self.dbCursor = self.dbConn.cursor()
                    timer = time.time()

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
                        data = self.dbCursor.execute("SELECT indexed FROM Files WHERE hash=?", (key,)).fetchone()
                        if data is None:
                            indexed = now
                        else:
                            indexed = data[0]

                        self.dbCursor.execute("INSERT OR REPLACE INTO Files VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                              (key, "1", name, path, size, ctime, mtime, indexed))
                except Exception as e:
                    logger.critical("Error while scan and update DB: " + str(e))


        self.dbConn.commit()
        self.dbCursor.execute("DELETE FROM Files WHERE removed = '0' ")
        logger.info("Final commit in sqlite scan thread #" + str(self.DBNumber))
        self.dbConn.commit()
        self.dbConn.execute("VACUUM")


class SearchInSqliteDB(QtCore.QThread):
    rowEmitted = QtCore.Signal(str, str, str, int, int, int)
    searchComplete = QtCore.Signal()
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
        # the loop and the piece after it forms such a string:
        # (SELECT ... FROM Files WHERE...) (UNION ALL SELECT ... FROM DB#.Files WHERE ...) (LIMIT ...)
        # loops:         ^first one                    ^second and others^        after loops^
        parameters = []
        for i in range(1, self.DBCount + 1):
            dbCursor = self.dbConn.cursor()
            # SQL TABLE: hash, removed, filename, path, size, created, modified, indexed
            if i == 1:
                query = "SELECT filename, path, size, created, modified, indexed FROM Files WHERE 1 "
            else:
                query += " UNION ALL SELECT filename, path, size, created, modified, indexed FROM DB" + str(i) + ".Files WHERE 1 "


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
                        #print(str(exts.index(ext)) + " " + str(len(exts) - 1))
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
                    minsize = self.filters["FilterMinSize"] + 1073741824

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
                    maxsize = self.filters["FilterMaxSize"] + 1073741824

                query += " AND (size <= ?)"
                parameters += [maxsize]
            # indexed in last days
            if self.filters["FilterIndexedLastDaysEnabled"]:
                filterInSeconds = self.filters["FilterIndexedLastDays"] * 86400
                queryTime = int(time.time()) - filterInSeconds
                query += " AND (Indexed > ?)"
                parameters += [queryTime]
        # limit
        if not self.filters["FilterShowMoreResultsEnabled"]:
            # I request one result more than a certain limit in the settings. If there are really more results,
            # their number can be compared with the limit in the function responsible for filling in a QTableWidget
            # (SearchInDBThreadRowEmitted), and showing the checkbox to disable the limit.
            limit = int(self.filters["FilterSearchLimit"]) + 1
            query += "LIMIT ?"
            parameters += [limit]

        query += ""  # for some cases )
        logger.debug("Execute search query with parameters: " + query + str(parameters))
        rows = dbCursor.execute(query, parameters).fetchall()
        counter = 0
        for row in rows:
            if not self._isRunning:  # this variable can be changed from main class for search interruption
                self.searchComplete.emit()
                return
            if counter > 500:
                counter = 0
                time.sleep(.2)
            counter += 1
            filename, path, size, ctime, mtime, indexed = row[0], row[1], row[2], row[3], row[4], row[5]

            # next one is needed because Signal cannot (?) emmit integer over 4 bytes,
            # so doubleconverted - in this place and in SearchInDBThreadRowEmitted()
            size = str(size)

            self.rowEmitted.emit(filename, path, size, ctime, mtime, indexed)

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

    def mySQLSearch(self):
        """Execute SQL query, emits values"""

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
            parameters += ["%" + utilities.mysql_query_wildficator(self.filters["FilterPath"]) + "%"]
        # extensions
        extFromFileName = utilities.get_extension_from_filename(self.filters["FilterFilename"].strip())
        # If a file name with a simple extension (contains only letters, numbers, and _) is specified,
        # the extension will be extracted from the name and the extension filter will be ignored in any case.
        if  re.match("[\w_]+$", extFromFileName):
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
                minsize = self.filters["FilterMinSize"] + 1073741824

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
                maxsize = self.filters["FilterMaxSize"] + 1073741824

            query += " AND (size <= %s)"
            parameters += [maxsize]
        # indexed in last days
        if self.filters["FilterIndexedLastDaysEnabled"]:
            filterInSeconds = self.filters["FilterIndexedLastDays"] * 86400
            queryTime = int(time.time()) - filterInSeconds
            query += " AND (Indexed > %s)"
            parameters += [queryTime]
        #limit
        if not self.filters["FilterShowMoreResultsEnabled"]:
            # I request one result more than a certain limit in the settings. If there are really more results,
            # their number can be compared with the limit in the function responsible for filling in a QTableWidget
            # (SearchInDBThreadRowEmitted), and showing the checkbox to disable the limit.
            limit = int(self.filters["FilterSearchLimit"]) +1
            query += "LIMIT %s"
            parameters += [limit]

        query += ""  # for some cases )
        logger.debug("Execute search query with parameters: " + query + str(parameters))
        dbCursor.execute(query, parameters)
        rows = dbCursor.fetchall()
        counter = 0
        for row in rows:
            if not self._isRunning:  # this variable can be changed from main class for search process interruption
                self.searchComplete.emit()
                return
            if counter > 500:
                counter = 0
                time.sleep(.2)
            counter += 1
            filename, path, size, ctime, mtime, indexed = row[0], row[1], row[2], row[3], row[4], row[5]

            # next one is needed because Signal cannot (?) emmit integer over 4 bytes,
            # so doubleconverted - in this place and in SearchInDBThreadRowEmitted()
            size = str(size)

            self.rowEmitted.emit(filename, path, size, ctime, mtime, indexed)
        self.dbConn.close()
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
        logger.info("Scan thread is started for MySQL. Thread #" + str(self.threadID) + ", path: " + self.path)

        self.open_connection()


        self.updateDB(self.path, self.removedKey)
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
            logger.critical("Thread #" + str(self.threadID) + ". MySQL connection error: " + str(e))
            self.sigIsOver.emit(self.threadID)
            self.exit()

    def execute_and_commit_to_db(self, sql, values):
        '''commit files to DB'''
        dbCursor = self.dbConn.cursor()
        try:
            dbCursor.executemany(sql, values)
            self.dbConn.commit()
        except Exception as e:
            logger.critical("MySQL execute and commit error: " + str(e))
        dbCursor.close()

    def updateDB(self, rootpath, removedKey):
        """Scan filesystem from given path"""
        if isWindows and not utilities.str2bool(self.settings.value("disableWindowsLongPathSupport")):
            self.windowsLongPathHack = True
        else:
            self.windowsLongPathHack = False

        if self.windowsLongPathHack:
            rootpath = "\\\\?\\" + rootpath

        filesIndexed = 0

        sqlTransactionLimit = 20000
        sqlTransactionCounter = 0
        varsArr = []
        sql = "insert into `Files` (hash, removed, filename, type, path, size, created, modified, indexed)" \
              " values(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE size=values(size), modified=values(modified), removed=values(removed)"

        for entry in utilities.scantree(rootpath):
            # commit to DB every N (sqlTransactionLimit) files
            if sqlTransactionCounter >= sqlTransactionLimit:
                logger.debug("Thread #" + str(self.threadID) + ", starting commit to MySQL. Files indexed: " + str(filesIndexed))
                self.execute_and_commit_to_db(sql, varsArr)

                logger.debug("Thread #" + str(self.threadID) + ", comitted to MySQL. Files indexed: " + str(filesIndexed))
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

        logger.debug("Thread #" + str(self.threadID) + ", starting FINAL commit to MySQL. Files indexed: " + str(
            filesIndexed))
        self.execute_and_commit_to_db(sql, varsArr)
        logger.info("Thread #" + str(self.threadID) + " FINAL commit complete. Files indexed (total in thread):" + str(filesIndexed))



# DIALOG CLASSES
class AboutDialog(QtWidgets.QDialog, pyAbout.Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " - About")
        self.versionLabel.setText("(v. " + __version__ + ")")


class OpenLogDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)

        self.setWindowTitle(__appname__ + " - LogFile:" + str(logfile))
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)

        logtext = str(logfile) + ":\n\r\n\r"

        with open(logfile, 'r') as infile:
            for line in infile:
                logtext +=  line

        layout = QtWidgets.QVBoxLayout()
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textEdit.setText(logtext)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)


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

        indx = self.PREFLoggingLevel.findText(initValues["LogLevel"])
        self.PREFLoggingLevel.setCurrentIndex(indx)



def unhandled_exception(exc_type, exc_value, exc_traceback):
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)


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