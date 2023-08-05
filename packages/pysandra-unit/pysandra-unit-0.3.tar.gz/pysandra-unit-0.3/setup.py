from setuptools import setup

import pysandraunit

setup(name='pysandra-unit',
      version='0.3',
      author='Jure Ham',
      license='GPLv3',
      author_email='jure.ham@zemanta.com',
      description="Python wrapper for cassandra-unit.",
      url='https://github.com/Zemanta/pysandra-unit',
      packages=['pysandraunit', 'pysandraunit.django',],
      package_data={
        'pysandraunit': ['jar/pysandra-unit.jar', 'resources/cu-cassandra.yaml'],
      },
      install_requires=[
        'pyyaml',
      ],
      long_description=pysandraunit.__doc__,
      include_package_data=True,
      platforms='any',
      zip_safe=True)
