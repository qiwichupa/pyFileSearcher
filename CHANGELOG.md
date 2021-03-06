# Changelog

## 1.1.1
* fix: saving the pid process to a pid file. Additional verification reduces the chance of stopping scan execution when the pid file has not been deleted.
* other: default "sqlTransactionLimit" changed from 20000 to 1000

## 1.1.0
* feature: saving information about deleted files, searching them
* feature: fast calculation of the size of the directory (with subdirectories) according to data from the database
* feature: the function of copying selected rows to the clipboard
* ui: human format (1024 -> 1KiB, etc.) for the size of files in the result table
* ui: "stop" function for "search" button
* ui: transaction limit for mysql added to preferences
* fix: locking the filter save button after saving and clearing the filter name field
* fix: now the search in the sqlite database does not provide duplicates if the databases index the same or intersecting directories
* fix: corrected request value for Gb size modifier
* fix: an incorrect variable caused an exception if there is a problem with working with MySQL.
* other: utf-8 in log, settings, csv export
* other: threaded file existence check for smoother scrolling of search results
* other: smoother update of search results
