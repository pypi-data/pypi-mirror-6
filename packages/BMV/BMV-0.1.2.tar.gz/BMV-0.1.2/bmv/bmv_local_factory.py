from bmv_local_csv    import BMVLocalCSV
from bmv_local_sqlite import BMVLocalSqlite

class Formats(object):
	CSV = "CSV"
	SQLITE = "SQLITE"

class BMVLocalFactory(object):
	"""Help to generalize the storage of BMV data"""

	@staticmethod
	def factory(format, file, data):
		"""Performs storage methods

		Keyword arguments:

        format -- How to store the data
        file   -- Where to store data
        data   -- The data to store

		"""

		if format == Formats.SQLITE:
			BMVLocalSqlite.store(file, data)
		else: #Formats.CSV or None
			BMVLocalCSV.store(file, data)

if __name__ == '__main__':
    help(BMVLocalFactory)