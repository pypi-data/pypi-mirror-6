import shelve
import os


def open_shelve():
    # create dir if not exists
    try:
        os.makedirs(os.getenv("HOME") + '/.xboomx')
    except:
        pass

    # open shelve
    return shelve.open(os.getenv("HOME") + '/.xboomx/xboomx.db')
