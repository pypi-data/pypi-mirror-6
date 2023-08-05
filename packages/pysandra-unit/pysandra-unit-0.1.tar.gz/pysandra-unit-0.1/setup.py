from setuptools import setup

setup(name='pysandra-unit',
      version='0.1',
      author='Jure Ham',
      license='GPLv3',
      author_email='jure.ham@zemanta.com',
      description="Python wrapper for cassandra-unit.",
      url='https://github.com/Zemanta/pysandra-unit',
      packages=['pysandraunit',],
      package_data={
        'pysandraunit': ['jar/pysandra-unit.jar'],
      },
      include_package_data=True,
      platforms='any',
      zip_safe=True)
