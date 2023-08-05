import subprocess
import os
import json

_here = lambda x: os.path.join(os.path.dirname(os.path.abspath(__file__)), x)

_PYSANDRA_COMMAND_START = 'start'
_PYSANDRA_COMMAND_LOAD_DATA = 'load'
_PYSANDRA_COMMAND_CLEAN_DATA = 'clean'

_PYSANDRA_JAR_PATH = _here('jar/pysandra-unit.jar')


class PysandraUnitServerError(Exception): pass

class PysandraUnit(object):

	_dataset_path = None
	_server = None

	def __init__(self, dataset_path):
		self._dataset_path = dataset_path

	def _run_pysandra(self):
		self._server = subprocess.Popen(["java", "-jar", _PYSANDRA_JAR_PATH], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

	def _run_command(self, command, param=''):
		msg = {
			'command': command,
			'param': param,
		}
		self._server.stdin.write('%s\n' % json.dumps(msg))

		try:
			response_str = self._server.stdout.readline().strip()
			response = json.loads(response_str)
		except Exception:
			raise PysandraUnitServerError('Invalid pysandra server response: %s' % response_str)

		if response.get('status') == 'ok':
			return response.get('value');

		raise PysandraUnitServerError(response)

	def start(self):
		self._run_pysandra()

		server = self._run_command(_PYSANDRA_COMMAND_START)
		self._run_command(_PYSANDRA_COMMAND_LOAD_DATA, self._dataset_path)

		return [server]

	def clean(self):
		if not self._server:
			raise PysandraUnitServerError('Server has not been started')

		self._run_command(_PYSANDRA_COMMAND_CLEAN_DATA)
		self._run_command(_PYSANDRA_COMMAND_LOAD_DATA, self._dataset_path)

