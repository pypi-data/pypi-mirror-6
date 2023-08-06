#!/usr/bin/python

import sqlite3

class BMVLocalSqlite(object):
    """An interface to store BMV data to a sqlite database"""

    TABLE_NAME = "BMV"

    @staticmethod
    def store(fileName, bmv_data):
        """Stores BMV data into the Sqlite filename

        Keyword arguments:

        fileName -- Where to store data
        bmv_data -- The data to store
        """

        con = sqlite3.connect(fileName)

        cur = con.cursor()

        columns  = ', '.join(bmv_data.keys())

        i = 0
        values = []
        for column in bmv_data.keys():
            values.insert(i, bmv_data[column])
            i = i + 1

        cur.execute(
            "INSERT INTO "+ BMVLocalSqlite.TABLE_NAME 
            + "("+ columns +")"
            + " VALUES("+ ', '.join(values) +")"
        )

        con.commit()


if __name__ == '__main__':
    help(BMVLocalSqlite)