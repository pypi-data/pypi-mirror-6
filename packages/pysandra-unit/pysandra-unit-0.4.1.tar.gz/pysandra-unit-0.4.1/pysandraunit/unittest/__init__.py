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

	def __call__(self, result=None):
		"""Django does this"""

		testMethod = getattr(self, self._testMethodName)
		skipped = (getattr(self.__class__, "__unittest_skip__", False) or getattr(testMethod, "__unittest_skip__", False))

		if not skipped:
			self._start_cassandra()

		super(CassandraTestCase, self).__call__(result)

		if not skipped:
			self._clean_cassandra()
