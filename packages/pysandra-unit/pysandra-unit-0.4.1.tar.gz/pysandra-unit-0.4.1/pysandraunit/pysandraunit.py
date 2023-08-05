import subprocess
import os
import json
import yaml
import shutil
import pkg_resources

__all__ = ['PysandraUnit', 'PysandraUnitServerError']

_COMMAND_START = 'start'
_COMMAND_STOP = 'stop'
_COMMAND_LOAD_DATA = 'load'
_COMMAND_CLEAN_DATA = 'clean'

_DEFAULT_CASSANDRA_HOST = 'localhost'
_DEFAULT_RPC_PORT = 9171
_DEFAULT_NATIVE_TRANSPORT_PORT = 9142

_TMP_PATHS = ['/dev/shm/', '/tmp/', './']
_TMP_DIR = 'pysandraunittarget/'

_JAR_PATH = 'jar/pysandra-unit.jar'
_CASSANDRA_YAML_PATH = 'resources/cu-cassandra.yaml'

_SUPPORTED_DATASET_FORMATS = ['yaml', 'xml', 'cql', 'json']

_CASSANDRA_YAML_REL_PATH = 'cassandra.yaml'
_CASSANDRA_DIR_OPTIONS = {
	'commitlog_directory': 'embeddedCassandra/commitlog',
	'saved_caches_directory': 'embeddedCassandra/saved_caches',
	'data_file_directories': ['embeddedCassandra/data'],
}


class PysandraUnitServerError(Exception): pass

class PysandraUnit(object):
	"""
	Construct a PysandraUnit object. Java server won't be started yet

	:param dataset_path: path to the dataset file. Check cassandra-unit docs for details
	:param tmp_dir: path to the directory where PysandraUnit and Cassandra should create temporary files
	:param rpc_port: Cassandra rpc port
	:param native_transport_port: Cassandra native transport port
	:param cassandra_yaml_options: dict of additional options passed to Cassandra in cassandra.yaml file
	"""

	_dataset = None
	_server = None
	_cassandra_yaml = None

	_cassandra_running = False

	tmp_dir = None
	rpc_port = None
	native_transport_port = None

	def __init__(self, dataset_path=None, tmp_dir=None, rpc_port=None, native_transport_port=None, cassandra_yaml_options=None):
		self._dataset = self._parse_dataset_file_path(dataset_path)

		self.tmp_dir = tmp_dir or self._find_tmp_dir()
		self._create_tmp_dir()

		pkg_resources.set_extraction_path(self.tmp_dir)
		self._here = lambda x: pkg_resources.resource_filename('pysandraunit', x)

		self.rpc_port = rpc_port or _DEFAULT_RPC_PORT
		self.native_transport_port = native_transport_port or _DEFAULT_NATIVE_TRANSPORT_PORT

		self._cassandra_yaml = self._get_yaml_file(cassandra_yaml_options)

	def _create_tmp_dir(self):
		if os.path.exists(self.tmp_dir):
			if not os.access(self.tmp_dir, os.W_OK):
				raise PysandraUnitServerError('Directory %s exists but is not writable by the current user' % self.tmp_dir)
			shutil.rmtree(self.tmp_dir)
		os.makedirs(self.tmp_dir, 0o755)

	def _find_tmp_dir(self):
		for path in _TMP_PATHS:
			if not os.path.exists(path):
				continue
			if not os.path.isdir(path):
				continue
			if not os.access(path, os.W_OK):
				continue

			full_path = os.path.join(path, _TMP_DIR)
			return full_path

		return None

	def _parse_dataset_file_path(self, path):
		if not path:
			return None

		extension = os.path.splitext(path)[1].split('.')[-1]
		if extension not in _SUPPORTED_DATASET_FORMATS:
			raise PysandraUnitServerError('Unsupported dataset file type')

		return (path, extension)

	def _get_yaml_file(self, yaml_options):
		config = yaml.load(open(self._here(_CASSANDRA_YAML_PATH), 'r'))

		for opt, c_dirs in _CASSANDRA_DIR_OPTIONS.iteritems():
			if isinstance(c_dirs, list):
				config[opt] = [os.path.join(self.tmp_dir, c_dir) for c_dir in c_dirs]
			else:
				config[opt] = os.path.join(self.tmp_dir, c_dirs)

		config['rpc_port'] = self.rpc_port
		config['native_transport_port'] = self.native_transport_port

		if yaml_options:
			for k, v in yaml_options:
				config[k] = v

		new_yaml_path = os.path.join(self.tmp_dir, _CASSANDRA_YAML_REL_PATH)

		with open(new_yaml_path, 'w') as fw:
			fw.write(yaml.dump(config, default_flow_style=False))

		return new_yaml_path

	def _run_pysandra(self):
		self._server = subprocess.Popen(["java", "-jar", self._here(_JAR_PATH)], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

	def _get_command_message(self, msg):
		return '%s\n' % json.dumps(msg)

	def _run_command(self, command, param=None, join=False):
		if not self._server or self._server.stdin.closed or self._server.stdout.closed:
			raise PysandraUnitServerError('Pysandra server not running')

		msg = {
			'command': command,
			'param': param or {},
		}

		if join:
			response_str = self._server.communicate(self._get_command_message(msg))[0].strip()
		else:
			self._server.stdin.write(self._get_command_message(msg))
			response_str = self._server.stdout.readline().strip()

		if not response_str:
			try:
				error_msg = self._server.stderr.readline()
			except ValueError:
				error_msg = 'Unknown error'
			raise PysandraUnitServerError('Failed to execute command %s: %s' % (command, error_msg))

		try:
			response = json.loads(response_str)
		except Exception:
			raise PysandraUnitServerError('Invalid pysandra server response: %s' % response_str)

		if response.get('status') == 'ok':
			return response.get('value');

		raise PysandraUnitServerError(response)

	def get_cassandra_host(self):
		"""
		Returns Cassandra server host and rpc port in format: 'localhost:9710'
		"""

		return '%s:%s' % (_DEFAULT_CASSANDRA_HOST, self.rpc_port)

	def load_data(self, dataset_path=None):
		"""
		Load schema into Cassandra from dataset file
		If file isn't provided the one from constructior will be used

		:param dataset_path: path to the dataset file. Check cassandra-unit docs for details
		"""

		if dataset_path:
			dataset = self._parse_dataset_file_path(dataset_path)
		else:
			dataset = self._dataset

		if not dataset:
			raise PysandraUnitServerError('Can\'t load data. No dataset specified.')

		self._run_command(_COMMAND_LOAD_DATA, {
			'filename': dataset[0],
			'type': dataset[1],
			'host': _DEFAULT_CASSANDRA_HOST,
			'rpc_port': self.rpc_port,
			'native_transport_port': self.native_transport_port,
		})

	def start(self):
		"""
		Start Pysandra and Cassandra server, loads dataset file if provided in the constructor
		If server is already running, 'PysandraUnitServerError' exception will be raised
		"""

		if self._cassandra_running:
			raise PysandraUnitServerError('Cassandra server already running')

		self._run_pysandra()

		self._run_command(_COMMAND_START, {
			'tmpdir': self.tmp_dir,
			'yamlconf': self._cassandra_yaml,
		})

		if self._dataset:
			self.load_data();

		self._cassandra_running = True

		return [self.get_cassandra_host()]

	def stop(self):
		"""
		Stop Pysandra and Cassandra server if running
		"""

		if self._cassandra_running:
			self._run_command(_COMMAND_STOP, join=True)

		self._server = None
		self._cassandra_running = False

	def clean(self):
		"""
		Cleans all Cassandra Keyspaces and reloads data if dataset is provided in constructor
		If server is not running, 'PysandraUnitServerError' exception will be raised
		"""

		if not self._cassandra_running:
			raise PysandraUnitServerError('Cassandra server not running')

		self._run_command(_COMMAND_CLEAN_DATA)
		if self._dataset:
			self.load_data();
