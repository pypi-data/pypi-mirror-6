"""
	Django CassandraTestCase
	~~~~~~~~~~~~~~~~~~~~~~~~

	Django TestCase which starts Cassandra server on the first setUp and reloads data for every test case
"""

__all__ = ['CassandraTestCase', 'CassandraTestCaseConfigException']

from django.test import TestCase
from django.conf import settings

from pysandraunit.testcasebase import CassandraTestCaseBase
from pysandraunit.testcasebase import CassandraTestCaseConfigException


class CassandraTestCase(CassandraTestCaseBase, TestCase):

	def _pre_setup(self):
		if hasattr(super(CassandraTestCaseBase, self), '_pre_setup'):
			super(CassandraTestCaseBase, self)._pre_setup()

		self._start_cassandra()

	def _post_teardown(self):
		if hasattr(super(CassandraTestCaseBase, self), '_post_teardown'):
			super(CassandraTestCaseBase, self)._post_teardown()

		self._clean_cassandra()

CassandraTestCase.set_global_settings(settings)
