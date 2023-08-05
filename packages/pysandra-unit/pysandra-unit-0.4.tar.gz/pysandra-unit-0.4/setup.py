"""
	pysandra-unit
	~~~~~

	Python wrapper around cassandra-unit that helps you write isolated unittests in Django and other python applications.
"""

from setuptools import setup


setup(name='pysandra-unit',
      version='0.4',
      author='Jure Ham',
      license='GPLv3',
      author_email='jure.ham@zemanta.com',
      description="Python wrapper for cassandra-unit.",
      url='https://github.com/Zemanta/pysandra-unit',
      packages=['pysandraunit','pysandraunit.django','pysandraunit.unittest',],
      package_data={
        'pysandraunit': ['jar/pysandra-unit.jar', 'resources/cu-cassandra.yaml'],
      },
      install_requires=[
        'pyyaml',
      ],
      long_description=__doc__,
      include_package_data=True,
      platforms='any',
      zip_safe=True)
