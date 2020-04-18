import sqlite3


def getConnection():
    return sqlite3.connect("cinema.db", check_same_thread=False)
