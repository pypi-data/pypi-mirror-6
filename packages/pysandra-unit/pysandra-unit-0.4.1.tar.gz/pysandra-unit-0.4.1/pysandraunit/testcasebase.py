from pysandraunit import PysandraUnit

_pysandra_singleton = None
_pysandra_settings_singleton = None


class CassandraTestCaseConfigException(Exception):
	pass

class CassandraTestCaseBase(object):
	"""
	Django TestCase which starts Cassandra server on the first setUp and reloads data for every test case
	"""

	cassandra_server_list = None

	@classmethod
	def set_global_settings(cls, settings):
		"""
		Set pysandraunit settings

		:param settings: module or class with pysandraunit configuration

		Accepted options are:

		PYSANDRA_SCHEMA_FILE_PATH = 'path_to_schema'

		PYSANDRA_TMP_DIR = '/tmp/path'

		PYSANDRA_RPC_PORT = port

		PYSANDRA_NATIVE_TRANSPORT_PORT = port

		PYSANDRA_CASSANDRA_YAML_OPTIONS = {}
		"""
		global _pysandra_settings_singleton

		_pysandra_settings_singleton = settings


	def _init_cassandra(self):
		global _pysandra_singleton

		if not _pysandra_settings_singleton:
			_pysandra_singleton = PysandraUnit()
		else:
			schema_path = getattr(_pysandra_settings_singleton, 'PYSANDRA_SCHEMA_FILE_PATH', None)
			tmp_dir = getattr(_pysandra_settings_singleton, 'PYSANDRA_TMP_DIR', None)
			rpc_port = getattr(_pysandra_settings_singleton, 'PYSANDRA_RPC_PORT', None)
			native_transport_port = getattr(_pysandra_settings_singleton, 'PYSANDRA_NATIVE_TRANSPORT_PORT', None)
			cassandra_yaml_options = getattr(_pysandra_settings_singleton, 'PYSANDRA_CASSANDRA_YAML_OPTIONS', None)

			_pysandra_singleton = PysandraUnit(schema_path, tmp_dir, rpc_port, native_transport_port, cassandra_yaml_options)

		return _pysandra_singleton.start()


	def _start_cassandra(self):
		global _pysandra_singleton

		if not _pysandra_singleton:
			self.cassandra_server_list = self._init_cassandra()
		else:
			self.cassandra_server_list = [_pysandra_singleton.get_cassandra_host()]

	def _clean_cassandra(self):
		if not _pysandra_singleton:
			return

		_pysandra_singleton.clean()

