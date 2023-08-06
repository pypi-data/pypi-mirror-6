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
        csv_file = open(fileName,'a')

        columns  = ', '.join(bmv_data.keys())

        values = []
        for column in bmv_data.keys():
            values.append(str(bmv_data[column]))

        #if the file is empty, write the headers
        if os.stat(fileName).st_size <= 0:
            csv_file.write(columns + "\n")

        #write the row to a csv
        csv_file.write(','.join(values) + "\n")

        #close the file
        csv_file.close()

if __name__ == '__main__':
    help(BMVLocalCSV)
