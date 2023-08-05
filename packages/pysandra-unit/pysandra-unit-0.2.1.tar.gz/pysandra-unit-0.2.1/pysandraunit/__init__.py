import os

from pysandraunit import PysandraUnit, PysandraUnitServerError

if os.environ.get('DJANGO_SETTINGS_MODULE'):
	from pysandraunit_django.testcase import CassandraTestCase, CassandraTestCaseConfigException
