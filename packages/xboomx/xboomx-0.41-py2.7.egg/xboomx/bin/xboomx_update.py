#!/usr/bin/python
import fileinput
import xboomx.db


def main():
    # open db
    db = xboomx.db.open_shelve()

    # get item to update
    item = fileinput.input().next()
    item = item.strip('\n')

    # update item
    db[item] = db.get(item, 0) + 1

    # print it
    print item

    # clean up
    db.sync()
    db.close()


main()
