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

	_settings=settings
	cassandra_server_list = None

