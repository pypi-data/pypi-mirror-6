import os

from django.conf import settings
from django.test import TestCase

from pysandraunit import PysandraUnit


_pysandra_single = None
_cassandra_server_list = None


class CassandraTestCaseConfigException(Exception):
	pass

class CassandraTestCase(TestCase):

	def _init_cassandra(self):
		global _pysandra_single

		if not hasattr(settings, 'PYSANDRA_SCHEMA_FILE_PATH') or not settings.PYSANDRA_SCHEMA_FILE_PATH:
			raise CassandraTestCaseConfigException('Missing PYSANDRA_SCHEMA_FILE_PATH setting')

		schema_path = settings.PYSANDRA_SCHEMA_FILE_PATH

		if not os.path.exists(schema_path):
			raise CassandraTestCaseConfigException('File %s doesn\'t exist' % schema_path)

		_pysandra_single = PysandraUnit(schema_path)
		return _pysandra_single.start()


	def _start_cassandra(self):
		global _pysandra_single, _cassandra_server_list

		if not _pysandra_single:
			_cassandra_server_list = self._init_cassandra()

		self.cassandra_server_list = _cassandra_server_list

	def _clean_cassandra(self):
		if not _pysandra_single:
			return

		_pysandra_single.clean()

	def _pre_setup(self):
		super(CassandraTestCase, self)._pre_setup()

		self._start_cassandra()

	def _post_teardown(self):
		super(CassandraTestCase, self)._post_teardown()

		self._clean_cassandra()
