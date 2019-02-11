
#!/usr/bin/env python3.7

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

import send2trash

import sys
import os
import sqlite3
import platform
import datetime
import time
import pathlib
import subprocess
from hashlib import md5

import utilities

from ui_files import pyMain
from ui_files import pyPreferences

__appname__ = "pyFileSearcher"
appDataPath = os.getcwd() + "/"
scanPIDFile = appDataPath + "scan.pid"
if len(sys.argv) <= 1 or  sys.argv[1] != "--scan":
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

        self.setWindowTitle(__appname__)

        self.settings = QtCore.QSettings(appDataPath + "settings.ini", QtCore.QSettings.IniFormat)

        # Menu items
        self.actionPreferences.triggered.connect(self.actionPreferencesEmitted)
        self.actionStartScan.triggered.connect(self.updateDBEmitted)

        # Search Tab
        FilterFilenameValidator = QtGui.QRegExpValidator("([\w \.\*\?])*")
        self.FilterFilename.setValidator(FilterFilenameValidator)
        self.FilterFilename.textEdited.connect(self.FilterFilenameTextChanged)
        FilterFileTypesValidator = QtGui.QRegExpValidator("([a-z0-9]{1,8},)*")
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

        # Search Tab - Filter List
        FilterListLineEditalidator = QtGui.QRegExpValidator("([a-z0-9_-])*")
        self.FilterListLineEdit.setValidator(FilterListLineEditalidator)

        self.FilterListSaveButton.setDisabled(True)

        self.FilterListLineEdit.textEdited.connect(self.FilterListLineEditEditedEmitted)

        self.FilterListSaveButton.clicked.connect(self.FilterListSaveButtonEmitted)
        self.FilterListRemoveButton.clicked.connect(self.FilterListRemoveButtonEmitted)
        self.FilterListComboBox.activated.connect(self.FilterListComboBoxEmitted)



        # Database Tab
        DBFileTypeFilterValidator = QtGui.QRegExpValidator("(^[,])?([a-z0-9]{1,8},)*")
        self.DBFileTypeFilter.setValidator(DBFileTypeFilterValidator)

        self.DBSelectDatabase.activated.connect(self.select_db)
        self.DBCount.valueChanged.connect(self.dbCountEmitted)

        self.DBFileTypeFilter.textEdited.connect(self.DBFileTypeFilterEmitted)
        self.DBFileTypeFilterMode.activated.connect(self.DBFileTypeFilterModeEmitted)
        self.DBRootScanPath.activated.connect(self.DBRootScanPathEmitted)

        self.DBApplySettingsButton.setDisabled(True)
        self.DBApplySettingsButton.clicked.connect(self.DBApplySettingsButtonEmitted)

        # Load Settings
        self.load_initial_settings()


        # Checking pid file of indexing process for locking some parts of interface
        self.load_pid_checker()

        # run scan with --scan parameter
        if isScanMode:
            if not os.path.isfile(scanPIDFile):
                print("Scan is running with command promt parameter!")
                self.updateDBEmitted()
            else:
                print("Scan is running already, check PID file. App closed.")
                self.exitActionTriggered()

    def tableFilesScrolled(self):
        """Checks the top and bottom visible lines in the file table, checks for files"""
        upRow = self.tableFiles.indexFromItem(self.tableFiles.itemAt(0, 0)).row()
        if self.tableFiles.itemAt(0, self.tableFiles.height()):
            downRow = self.tableFiles.indexFromItem(self.tableFiles.itemAt(0, self.tableFiles.height())).row()
        else:
            downRow = self.tableFiles.rowCount()

        for i in range(upRow, downRow):
            fullFilePath = self.tableFiles.item(i, self.tableFilesColumnPathIndx).text() + self.tableFiles.item(i, self.tableFilesColumnFilnameIndx).text()
            if not os.path.isfile(fullFilePath):
                for column in range(0, self.tableFiles.columnCount()):
                    self.tableFiles.item(i, column).setBackgroundColor("#ffa189")


    def load_initial_settings(self):
        """Loads initial settings from ini file and DBs"""

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
                self.DBSelectDatabase.setCurrentText("DB" + str(DBNumber))
        self.DBCount.setValue(DBCount)

# MAIN MENU ACTIONS
    def actionPreferencesEmitted(self):
        """Opens preferences dialog"""
        initValues = {"useExternalDatabase": self.settings.value("useExternalDatabase"),
                      "disableWindowsLongPathSupport": self.settings.value("disableWindowsLongPathSupport"),
                      "maxSearchResults": self.settings.value("maxSearchResults")
                      }
        dialog = PreferencesDialog(initValues)
        if dialog.exec_():
            self.settings.setValue("useExternalDatabase", utilities.bool2str(dialog.PREFUseExternalDB.isChecked()))
            self.settings.setValue("disableWindowsLongPathSupport",
                                   utilities.bool2str(dialog.PREFDisableWindowsLongPathSupport.isChecked()))
            self.settings.setValue("maxSearchResults", str(dialog.PREFMaxSearchResults.value()))

    def updateDBEmitted(self):
        """Starts scan filesystem and update database thread"""
        print(scanPIDFile)
        os.close(os.open(scanPIDFile, os.O_CREAT))

        self.updateDBThreads = {}

        for DBNumber in range(1, self.DBCount.value() + 1):
            self.updateDBThreads[DBNumber] = UpdateDBThread(DBNumber, self.settings)
            self.updateDBThreads[DBNumber].sigIsOver.connect(self.updateDBCompleted)
            self.updateDBThreads[DBNumber].start()
# MAIN MENU ACTIONS - END SECTION



# SAVE/LOAD FILTERS
    def FilterListSaveButtonEmitted(self):
        """Add or resave filter to settings"""
        filterName = self.FilterListLineEdit.text()
        if  filterName not in self.filters:
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

        self.settings.setValue("filters", ",".join(self.filters))

        self.FilterListLineEdit.setText("")
        self.FilterListComboBox.setCurrentText(filterName)


    def FilterListComboBoxEmitted(self):
        """Loads filter from settings"""

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
        self.FilterMinSizeEnabled.setChecked(utilities.str2bool(self.settings.value("FILTER_" + filterName + "/FilterMinSizeEnabled")))
        self.FilterMaxSize.setValue(int(self.settings.value("FILTER_" + filterName + "/FilterMaxSize")))
        self.FilterMaxSizeType.setCurrentIndex(int(self.settings.value("FILTER_" + filterName + "/FilterMaxSizeType")))
        self.FilterMaxSizeEnabled.setChecked(utilities.str2bool(self.settings.value("FILTER_" + filterName + "/FilterMaxSizeEnabled")))
        self.FilterIndexedLastDays.setValue(int(self.settings.value("FILTER_" + filterName + "/FilterIndexedLastDays")))
        self.FilterIndexedLastDaysEnabled.setChecked(utilities.str2bool(self.settings.value("FILTER_" + filterName + "/FilterIndexedLastDaysEnabled")))

        self.FilterFilenameTextChanged()

        self.FilterListLineEdit.setText(filterName)
        self.FilterListSaveButton.setEnabled(True)
        self.FilterListRemoveButton.setEnabled(True)


    def FilterListLineEditEditedEmitted(self):
        """Disable save filter button if filtername is empty"""
        if self.FilterListLineEdit.text() == "":
            self.FilterListSaveButton.setDisabled(True)
        else:
            self.FilterListSaveButton.setEnabled(True)

    def FilterListRemoveButtonEmitted(self):
        """Remove saved filter"""
        filterName = self.FilterListComboBox.currentText()


        self.filters.remove(filterName)
        self.FilterListComboBox.removeItem(self.FilterListComboBox.currentIndex())
        self.settings.remove("FILTER_" + filterName)
        self.settings.setValue("filters", ",".join(self.filters))
        if len(self.filters) == 0:
            self.FilterListRemoveButton.setDisabled(True)
# SAVE/LOAD FILTERS - END SECTION

    def select_db(self, DBNumber, runViaGUI=True):
        """Load settings from sqlite database to GUI, return DB name for combobox"""
        if runViaGUI is True:
            DBNumber = DBNumber + 1

        self.dbConn[DBNumber] = sqlite3.connect(get_db_path(DBNumber))

        try:
            dbCursor = self.dbConn[DBNumber].cursor()

            keys = ("RootPath", "Exclusions", "ExclusionsMode")
            dbOptions = {}
            for key in keys:
                dbOptions[key] = dbCursor.execute("SELECT value FROM Settings WHERE option=?", (key,)).fetchall()[0][0]

            self.DBFileTypeFilterMode.setCurrentText(dbOptions["ExclusionsMode"])
            self.DBFileTypeFilter.setText(dbOptions["Exclusions"])
            self.DBRootScanPath.setItemText(0, dbOptions["RootPath"] if dbOptions["RootPath"] else "[Path is not set]")


        except Exception as e:
            QtWidgets.QMessageBox.critical(self, __appname__, "Unable to load settings from database:\r\n'" +
                                           get_db_path(DBNumber) + "'\r\nError:\r\n" + str(e))
            exit(1)

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
            QtWidgets.QMessageBox.critical(self, __appname__, "Unable to remove database file:\r\n'" +
                                           get_db_path(DBNumber) + "'\r\nError:\r\n" + str(e))
            exit(1)

    def dbCountEmitted(self, newDBCount):
        """Looks into settings for current DB count and compare with new one.
           Runs creating or deleting databases and updates controls"""
        newDBCount = self.DBCount.value()
        oldDBCount = int(self.settings.value("DBCount"))
        if newDBCount > oldDBCount:
            for i in range(oldDBCount + 1, newDBCount + 1):
                self.create_db(i)
                if self.select_db(i, False):
                    self.DBSelectDatabase.addItem("DB" + str(i))
                    self.DBSelectDatabase.setCurrentText("DB" + str(i))
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
        """Sets Apply button active when ExclusionsMode (Whitelist|Blacklist) was selected"""
        self.DBApplySettingsButton.setEnabled(True)

    def DBRootScanPathEmitted(self):
        """Sets Apply button active when path was selected, and sets path into first slot in combobox"""
        if self.DBRootScanPath.currentIndex() is 1:
            currentPath = self.DBRootScanPath.itemText(0)
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", currentPath)
            if path:
                path = QtCore.QDir.toNativeSeparators(path)
                self.DBRootScanPath.setItemText(0, path)
                self.DBApplySettingsButton.setEnabled(True)
            self.DBRootScanPath.setCurrentIndex(0)

    def DBApplySettingsButtonEmitted(self):
        """DB Apply Settings button was pressed - saving DB properties"""
        self.DBSelectDatabase.setDisabled(True)
        currentDB = self.DBSelectDatabase.currentIndex() + 1
        dbSettings = {}
        dbSettings["DBFileTypeFilter"] = self.DBFileTypeFilter.text()
        dbSettings["DBFileTypeFilterMode"] = self.DBFileTypeFilterMode.currentText()
        dbSettings["DBRootScanPath"] = self.DBRootScanPath.itemText(0)

        self.saveDBSettingsThread = SaveDBSettingsThread(currentDB, dbSettings)
        self.saveDBSettingsThread.settingsSavedSig.connect(self.saveDBSettingsThreadSavedSigEmitted)
        self.saveDBSettingsThread.start()

    def saveDBSettingsThreadSavedSigEmitted(self, DBNumber):
        """Reread db settings and unlocks interface when db settings was saved"""
        self.select_db(DBNumber, False)
        self.DBSelectDatabase.setEnabled(True)
        self.DBApplySettingsButton.setDisabled(True)
        self.DBSelectDatabase.setFocus()


    def updateDBCompleted(self, DBNumber):
        """Actions after update database is complete"""
        self.updateDBThreads[DBNumber].wait()
        del self.updateDBThreads[DBNumber]
        if len(self.updateDBThreads) == 0:
            os.remove(scanPIDFile)
            print("Scan is complete")
            if isScanMode:
                print("isScanMode - exit app")
                self.exitActionTriggered()

    def FilterFilenameTextChanged(self):
        """Does not allow search if filename filter is empty"""
        if self.FilterFilename.text().strip() == "":
            self.btnSearch.setDisabled(True)
        else:
            self.btnSearch.setEnabled(True)

    def btnSearchEmitted(self):
        """Runs searching process"""
        self.tableFiles.setRowCount(0)
        self.tableFiles.setSortingEnabled(False)

        # avoid double "press" via pressing enter in filter EditLines
        if not self.btnSearch.isEnabled():
            return

        self.btnSearch.setDisabled(True)

        self.btnSearch.setText("Searching...")

        time.sleep(.2)

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

        self.searchInDBThread = SearchInDB(self.DBCount.value(), filters)
        self.searchInDBThread.rowEmitted.connect(self.searchInDBThreadRowEmitted)
        self.searchInDBThread.searchComplete.connect(self.searchInDBThreadSearchCompleteEmitted)
        self.searchInDBThread.start()
        self.searchInDBThread.setPriority(QtCore.QThread.LowestPriority)

    def searchInDBThreadRowEmitted(self, filename, path, size, ctime, mtime, indexed):
        """While executing sql - gets returned rows and inserts them into QTableWidget
        Columns order in QTable:
        filename, type, size, modified, indexed, created, path"""
        row = self.tableFiles.rowCount()

        (ctime, mtime, indexed) = (str(datetime.datetime.fromtimestamp(ctime)),
                                   str(datetime.datetime.fromtimestamp(mtime)),
                                   str(datetime.datetime.fromtimestamp(indexed))
                                   )
        size = int(size)

        # limit
        if row > int(self.settings.value("maxSearchResults"))-1 and not self.FilterShowMoreResultsCheckbox.isChecked():
            self.FilterShowMoreResultsCheckbox.setVisible(True)
            self.FilterShowMoreResultsCheckbox.setText("Show more results (uncheck while searching to stop)")
            self.searchInDBThread._isRunning = False
            return

        self.tableFiles.insertRow(row)
        numItem = QtWidgets.QTableWidgetItem()
        numItem.setData(QtCore.Qt.EditRole, row+1)
        self.tableFiles.setItem(row, self.tableFilesColumnNumIndx, numItem)
        self.tableFiles.setItem(row, self.tableFilesColumnFilnameIndx, QtWidgets.QTableWidgetItem(filename))
        self.tableFiles.setItem(row, self.tableFilesColumnTypeIndx, QtWidgets.QTableWidgetItem(
            filename[filename.rfind(".") + 1:] if filename.rfind(".") != -1 else "")
                                # if there is a dot in filename - extract extension
                                )
        sizeItem = QtWidgets.QTableWidgetItem()
        sizeItem.setData(QtCore.Qt.EditRole, size)
        self.tableFiles.setItem(row, self.tableFilesColumnSizeIndx, sizeItem)
        self.tableFiles.setItem(row, self.tableFilesColumnModifiedIndx, QtWidgets.QTableWidgetItem(mtime))
        self.tableFiles.setItem(row, self.tableFilesColumnIndexedIndx, QtWidgets.QTableWidgetItem(indexed))
        self.tableFiles.setItem(row, self.tableFilesColumnCreatedIndx, QtWidgets.QTableWidgetItem(ctime))
        self.tableFiles.setItem(row, self.tableFilesColumnPathIndx, QtWidgets.QTableWidgetItem(path))


    def searchInDBThreadSearchCompleteEmitted(self):
        """Unlocks GUI elements and runs filecheck (file exists or was removed) after searching"""
        self.tableFiles.setSortingEnabled(True)
        self.btnSearch.setDisabled(False)
        self.btnSearch.setText("Search...")
        self.tableFilesScrolled()

    def checkScanPIDFileLoopEmitted(self, fileExists):
        """Disable db count changer while indexing process"""
        if fileExists:
            self.DBCount.setDisabled(True)
            self.DBCountLabel.setText("DB Count (locked, <font color=red>why?</font>): ")
            self.actionStartScan.setText("Scan in progress")
            self.actionStartScan.setDisabled(True)
        else:
            self.DBCount.setEnabled(True)
            self.DBCountLabel.setText("DB Count: ")
            self.actionStartScan.setText("Start scan")
            self.actionStartScan.setEnabled(True)

# TABLE CONTEXT MENU
    def tableMenu(self, event):
        """Create context menu for tableFiles widget"""
        self.menu = QtWidgets.QMenu(self)
        if len(self.tableFiles.selectedItems()) <= 8 and len(self.tableFiles.selectedItems()) > 0:
            menuOpenFolder = QtWidgets.QAction('Open Folder', self)
            menuOpenFolder.triggered.connect(self.menuOpenFolder)
            self.menu.addAction(menuOpenFolder)
        if len(self.tableFiles.selectedItems()) > 0:
            menuDeleteFiles = QtWidgets.QAction('Move to Trash', self)
            menuDeleteFiles.triggered.connect(self.menuDeleteFiles)
            # menuDeleteFiles.setDisabled(True)
            self.menu.addAction(menuDeleteFiles)


        self.menu.popup(QtGui.QCursor.pos())

    def menuOpenFolder(self, event):
        """Opens folders for seelcted files"""
        allItems = self.tableFiles.selectedItems()
        rows =  [allItems[x:x+8] for x in range(0, len(allItems), 8)]
        for row in rows:
            if isWindows:
                os.startfile(row[self.tableFilesColumnPathIndx].text())
            else:
                subprocess.Popen(["xdg-open", row[self.tableFilesColumnPathIndx].text()])

    def menuDeleteFiles(self, event):
        """Delete selected files"""

        allItems = self.tableFiles.selectedItems()
        rows = [allItems[x:x + 8] for x in range(0, len(allItems), 8)]
        for row in rows:
            send2trash.send2trash(row[self.tableFilesColumnPathIndx].text() + row[self.tableFilesColumnFilnameIndx].text())
        self.tableFilesScrolled()


# TABLE CONTEXT MENU - END SECTION

    def load_pid_checker(self):
        """Starts thread with infinite checking pid file of indexing process"""
        self.mycheckScanPIDFileLoopThread = CheckScanPIDFileLoopThread()
        self.mycheckScanPIDFileLoopThread.pidFileExists.connect(self.checkScanPIDFileLoopEmitted)
        self.mycheckScanPIDFileLoopThread.start()

    def exitActionTriggered(self):
        """Exit the application"""
        sys.exit()


class SaveDBSettingsThread(QtCore.QThread):
    settingsSavedSig = QtCore.Signal(int)

    def __init__(self, DBNumber, dbSettings, parent=None):
        QtCore.QThread.__init__(self)

        self.DBNumber = DBNumber
        self.dbSettings = dbSettings

    def run(self):
        print("1")
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
            QtWidgets.QMessageBox.critical(self, __appname__,
                                           "Unable to write option to DB" + str(self.DBNumber) + "\r\n" +
                                           "Error:\r\n" + str(e))


class SearchInDB(QtCore.QThread):
    rowEmitted = QtCore.Signal(str, str, str, int, int, int)
    searchComplete = QtCore.Signal()
    dbConn = {}
    _isRunning = True

    def __init__(self, DBCount, filters, parent=None):
        QtCore.QThread.__init__(self)

        self.DBCount = DBCount
        self.filters = filters


    def run(self):
        """Execute SQL query, emits values"""

        for i in range(1, self.DBCount + 1):
            self.dbConn[i] = sqlite3.connect(pathlib.Path(get_db_path(i)).as_uri() + "?mode=ro", uri=True)

        for i in range(1, self.DBCount + 1):
            dbCursor = self.dbConn[i].cursor()
            # SQL TABLE: hash, removed, filename, path, size, created, modified
            query = "SELECT filename, path, size, created, modified, indexed FROM Files WHERE 1 "
            parameters = []

            # # query constructor
            # filename
            if self.filters["FilterFilename"].strip() != "":
                query += " AND (UPPER(filename) GLOB UPPER(?)) "
                parameters += ["" + self.filters["FilterFilename"] + ""]
            # path
            if self.filters["FilterPath"].strip() != "":
                query += " AND (UPPER(path) GLOB UPPER(?)) "
                parameters += ["*" + self.filters["FilterPath"] + "*"]
            # extentions
            if self.filters["FilterFileTypes"].strip() != "":
                query += " AND ("
                exts = list(set(self.filters["FilterFileTypes"].split(",")))  # uniqify exts filter
                for ext in exts:
                    query += " UPPER(filename) GLOB UPPER(?) "
                    parameters += ["*." + ext]
                    if exts.index(ext) < len(exts) - 1:
                        print(str(exts.index(ext)) + " " + str(len(exts) - 1))
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

            query += ""  # for some cases )
            print(query + str(parameters))
            rows = dbCursor.execute(query, parameters).fetchall()
            counter = 0
            for row in rows:
                if not self._isRunning: # this variable can be changed from main class for search interruption
                    self.searchComplete.emit()
                    return
                if counter > 500:
                    counter = 0
                    time.sleep(.2)
                counter +=  1
                filename, path, size, ctime, mtime, indexed = row[0], row[1], row[2], row[3], row[4], row[5]

                # next one is needed because Signal cannot (?) emmit integer over 4 bytes,
                # so doubleconverted - in this place and in searchInDBThreadRowEmitted()
                size = str(size)

                self.rowEmitted.emit(filename, path, size, ctime, mtime, indexed)

        self.searchComplete.emit()


class CheckScanPIDFileLoopThread(QtCore.QThread):
    pidFileExists = QtCore.Signal(bool)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self)

    def run(self):
        while True:
            if os.path.isfile(scanPIDFile):
                self.pidFileExists.emit(True)
            else:
                self.pidFileExists.emit(False)
            time.sleep(1)


class UpdateDBThread(QtCore.QThread):
    sigIsOver = QtCore.Signal(int)

    def __init__(self, DBNumber, settings, parent=None):
        QtCore.QThread.__init__(self)

        self.settings = settings
        self.DBNumber = DBNumber

    def run(self):

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
                    print("closed")
                    time.sleep(0.1)
                    self.dbConn = sqlite3.connect(get_db_path(self.DBNumber))
                    self.dbCursor = self.dbConn.cursor()
                    timer = time.time()

                try:
                    name = entry.name
                    if name.rfind(".") != -1:
                        extension = name[name.rfind(".") + 1:]
                    else:
                        extension = ""

                    if (extension in exclusions and exclusionsMode == "Whitelist"
                    ) or (
                            extension not in exclusions and exclusionsMode == "Blacklist"
                    ) or (
                            len(exclusions) == 1 and exclusions[0] == ""
                    ):
                        fullname = entry.path # full path + filename
                        path = fullname[:-len(name)]
                        if self.windowsLongPathHack:
                            path = path[4:]
                        size = int(entry.stat().st_size)
                        mtime = int(entry.stat().st_mtime)
                        ctime = int(entry.stat().st_ctime)
                        now = int(time.time())
                        hash.update(fullname.encode())
                        key = hash.hexdigest()

                        # SQL TABLE: hash, removed, filename, path, size, created, modified
                        data = self.dbCursor.execute("SELECT indexed FROM Files WHERE hash=?", (key,)).fetchone()
                        if data is None:
                            indexed = now
                        else:
                            indexed = data[0]

                        self.dbCursor.execute("INSERT OR REPLACE INTO Files VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                              (key, "1", name, path, size, ctime, mtime, indexed))
                except Exception as e:
                    print("Error while scan and update DB: " + str(e))

        self.dbConn.commit()
        self.dbCursor.execute("DELETE FROM Files WHERE removed = '0' ")
        print("final commit")
        self.dbConn.commit()
        self.dbConn.execute("VACUUM")


class PreferencesDialog(QtWidgets.QDialog, pyPreferences.Ui_Dialog):

    def __init__(self, initValues, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(__appname__ + " - Preferences")

        self.PREFDisableWindowsLongPathSupport.setChecked(
            utilities.str2bool(initValues["disableWindowsLongPathSupport"]))
        self.PREFUseExternalDB.setChecked(utilities.str2bool(initValues["useExternalDatabase"]))
        self.PREFMaxSearchResults.setValue(int(initValues["maxSearchResults"]))


app = QtWidgets.QApplication(sys.argv)
form = Main()
if not isScanMode:
    form.show()

app.exec_()
