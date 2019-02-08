def str2bool(arg):
    return(str(arg).lower() in ["true", "0", "ok"])


def bool2str(arg):
    if arg:
        return("True")
    else:
        return("False")







def scantree(path):
    """Recursively yield DirEntry objects for given directory.
    Usage:
    for entry in scantree(path):
        print(entry.path)
    """
    from  os import scandir
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            try:
                yield entry
                yield from scantree(entry.path)
            except Exception as e:
                print("Scantree func error(dir): " + str(e))
        else:
            try:
                yield entry
            except Exception as e:
                print("Scantree func error(file): " + str(e))
