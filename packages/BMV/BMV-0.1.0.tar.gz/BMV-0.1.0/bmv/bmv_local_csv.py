#!/usr/bin/python

import os
import csv

"""
A storage interface for BMV data
"""

class BMVLocalCSV(object):
    """An interface to store BMV data to a CSV file"""

    @staticmethod
    def store(fileName, bmv_data):
        """Stores BMV data into the filename

        Keyword arguments:

        fileName -- Where to store data
        bmv_data -- The data to store
        """

        #open a file to store data into
        csv_file = open(fileName,'wb')

        columns  = ', '.join(bmv_data.keys())

        i = 0
        values = []
        for column in columns:
            values.insert(i, bmv_data[column])
            i = i + 1

        #an interface to write data to the file
        writer = csv.DictWriter(
            csv_file, 
            delimiter=',', 
            fieldnames=columns
        )

        #if the file is empty, write the headers
        if os.stat(fileName).st_size <= 0:
            writer.writerow(dict((fn,fn) for fn in bmv_data.valuename))

        #write the row to a csv
        writer.writerow(bmv_data)

        #close the file
        csv_file.close()

if __name__ == '__main__':
    help(BMVLocalCSV)
