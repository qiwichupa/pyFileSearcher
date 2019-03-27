* feature: saving information about deleted files, searching them
* feature: fast calculation of the size of the directory (with subdirectories) according to data from the database
* ui: human format (1024 -> 1KiB, etc.) for the size of files in the result table
* ui: "stop" function for "search" button
* fix: locking the filter save button after saving and clearing the filter name field
* fix: now the search in the sqlite database does not provide duplicates if the databases index the same or intersecting directories
* fix: corrected request value for Gb size modifier
* fix: an incorrect variable caused an exception if there is a problem with working with MySQL.
* other: utf-8 in log, settings, csv export
* other: threaded file existence check for smoother scrolling of search results
* other: smoother update of search results
