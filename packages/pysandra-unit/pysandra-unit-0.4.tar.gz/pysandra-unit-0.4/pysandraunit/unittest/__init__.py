"""
	Python unittest CassandraTestCase
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Python unittest TestCase which starts Cassandra server on the first setUp and reloads data for every test case
"""

__all__ = ['CassandraTestCase', 'CassandraTestCaseConfigException']

from unittest import TestCase

from pysandraunit.testcasebase import CassandraTestCaseBase
from pysandraunit.testcasebase import CassandraTestCaseConfigException


class CassandraTestCase(CassandraTestCaseBase, TestCase):

	_settings=None

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
		cls._settings = settings

	def __call__(self, result=None):
		"""Django does this"""

		testMethod = getattr(self, self._testMethodName)
		skipped = (getattr(self.__class__, "__unittest_skip__", False) or getattr(testMethod, "__unittest_skip__", False))

		if not skipped:
			self._pre_setup()

		super(CassandraTestCase, self).__call__(result)

		if not skipped:
			self._post_teardown()
