from pysandraunit import PysandraUnit

from django.test import TestCase
from django.conf import settings

_pysandra_single = None
_cassandra_server_list = None



class CassandraTestCaseConfigException(Exception):
	pass

class CassandraTestCase(TestCase):
	"""
	Django TestCase which starts Cassandra server on the first setUp and reloads data for every test case
	"""

	def _init_cassandra(self):
		global _pysandra_single

		schema_path = getattr(settings, 'PYSANDRA_SCHEMA_FILE_PATH', None)
		tmp_dir = getattr(settings, 'PYSANDRA_TMP_DIR', None)
		rpc_port = getattr(settings, 'PYSANDRA_RPC_PORT', None)
		cassandra_yaml_options = getattr(settings, 'PYSANDRA_CASSANDRA_YAML_OPTIONS', None)

		_pysandra_single = PysandraUnit(schema_path, tmp_dir, rpc_port, cassandra_yaml_options)

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
