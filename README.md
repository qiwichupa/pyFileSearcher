# pyFileSearcher
pyFileSearcher was designed to be lightweight, easy to use, but capable of handling a large volume of files tool. A tool that I personally could use on large corporate servers to find out - which files have taken all my space in the last few days? It's free, it's opensource, it's for linux and windows.

The program is written in Python 3 using the Qt5.

![main](https://user-images.githubusercontent.com/132103/55246962-76c89500-5257-11e9-93a3-991324614577.png)

## What are you getting
* Search by name, size, file type. Search by part of the path. Search for files listed in the index no earlier than N days ago
* Saving information about deleted files, searching for them as well as for regular files
* Ability to save search settings for future use
* Ability to save search results in csv
* Highlighting non-existent (deleted) files in search results
* Logging access errors - you will know which folders were not indexed for some reason
* Support for long paths (> 256 characters) in windows

## How it works
The program runs through your hard disk and saves the minimum necessary information about the files: size, time of creation, modification, and time of the first indexing of the file (convenient for finding new files without looking at the attributes). To store this information, you can use the sqlite database (one for each target directory you want to index), or the MySQL database if you want to index hundreds of thousands and millions of files. In the latter case, you can use only one database, but specify several target directories. In both cases, each target directory is indexed in parallel with the others.

After you have set up simple indexing parameters (target directories, and white or black lists of extensions in the case of using sqlite), you can run the program with the "--scan" parameter to automatically start indexing, after which the program will be closed. Use this key to run via the scheduler.

During the scanning process, a pid-file is created in the working ("data") directory. Its existence blocks the process of launching a scan, if the program crashed - remove it manually.

## Tests
The program was tested on a file server with about 20 million files. Scan time - about 5 hours. Files in biggest thread: ~7000000 

MySQL non-default (for debian stretch) parameters:

innodb_buffer_pool_size = 3000M

innodb_log_file_size = 128M

innodb_log_buffer_size = 4M

innodb_flush_method = O_DIRECT
