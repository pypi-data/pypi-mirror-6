'''
    Tinkerer-Localpost output
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Handles writing output

    :copyright: Copyright 2013, Nathan Hawkes
    :license: FreeBSD, see LICENCE file
'''
import logging


# output writer
write = logging.getLogger("write")

def init(quiet_mode, verbosity=2, logfile=None):
    """
    Initialize output based on quiet/filename-only flags
    """
    # set the logging level based on verbosity
    if not quiet_mode:
        if verbosity:
            if verbosity >= 0 and verbosity < 4:
                verbosity = verbosity + 2
            elif verbosity >= 4:
                verbosity = 6
        else:
            verbosity = 2
    else:
        verbosity = 2

    loglevel = (6 - verbosity) * 10

    # set up the default handlers
    lfile = None
    if logfile:
        try:
            lfile = logging.FileHandler(level=loglevel, stream=logfile)
        except IOError as ex:
            stream = logging.StreamHandler()
            stream.level = loglevel
            errMessage = "Failed to open %s. Reverting to the console logging." % logfile
    else:
        stream = logging.StreamHandler()
        stream.level = loglevel


    # if a FileHandler was requested and initialized, set up the FileHandler
    # and a StreamHandler on the console for errors
    if logfile and lfile:
        info = logging.StreamHandler()
        info.level = logging.ERROR
        write.addHandler(info)
        write.addHandler(lfile)

    # if the FileHandler was requested and not set up correctly default
    # to writing to the console and explain the problem
    elif logfile and stream:
        write.addHandler(stream)
        write.error(errMessage)

    # otherwise write to the console only
    else:
        write.addHandler(stream)

