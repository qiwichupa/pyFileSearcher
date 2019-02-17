def str2bool(arg):
    return(str(arg).lower() in ["true", "0", "ok"])


def bool2str(arg):
    if arg:
        return("True")
    else:
        return("False")





def mysql_query_wildficator(query):
    wild_query = query.replace("%", "\%").replace("_", "\_").replace("*", "%").replace("?", "_")
    return(wild_query)

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
                #yield entry
                yield from scantree(entry.path)
            except Exception as e:
                print(str(e))
        elif entry.is_file():
            try:
                yield entry
            except Exception as e:
                print(str(e))
        else:
            pass

class LoggerWriter:
    def __init__(self, level):
        # self.level is really like using log.debug(message)
        # at least in my case
        self.level = level

    def write(self, message):
        # if statement reduces the amount of newlines that are
        # printed to the logger
        if message != '\n':
            self.level(message)

    def flush(self):
        # create a flush method so things can be flushed when
        # the system wants to. Not sure if simply 'printing'
        # sys.stderr is the correct way to do it, but it seemed
        # to work properly for me.
        #self.level(sys.stderr)
        pass
