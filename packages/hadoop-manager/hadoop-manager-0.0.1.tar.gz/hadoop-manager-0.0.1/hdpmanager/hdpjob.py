import os
import re
import cPickle as pickle

import subprocess

from hdpenv import HadoopEnv

ZHDUTILS_PACKAGE = 'hdpmanager'
EGG_NAME = 'zemanta_hadoop_job'
EGG_VERSION = '1.0'

DEFAUT_NUM_REDUCERS = 10

HADOOP_STREAMING_JAR_RE = re.compile(r'^hadoop.*streaming.*\.jar$')

CONF_PICKE_FILE_PATH = 'streamer_conf.pickle'
SERIALIZATION_CONF_PICKE_FILE_PATH = 'serialization_conf.pickle'


class HadoopJob(object):
	"""
	HadoopJob object for managing mapreduce jobs
	Create it with the HadoopManager.create_job methos
	"""

	def __init__(self, hdp_manager, input_paths, output_path, mapper, reducer=None, combiner=None, num_reducers=None, serialization=None, job_env=None, conf=None, root_package=None):

		self._hdpm = hdp_manager

		self._input_paths = input_paths
		self._output_path = output_path

		self._root_package = root_package

		self._mapper = mapper
		self._combiner = combiner
		self._reducer = reducer
		self._num_reducers = num_reducers or DEFAUT_NUM_REDUCERS

		self._serialization_conf = serialization
		self._serialization_conf_file = self._create_conf_file(serialization, SERIALIZATION_CONF_PICKE_FILE_PATH)

		self._conf = conf
		self._conf_file = self._create_conf_file(conf, CONF_PICKE_FILE_PATH)

		self._hadoop_env = HadoopEnv(hdp_manager, root_package=self._root_package, **(job_env or {}))

	def _create_conf_file(self, conf, fp):
		if not conf:
			return

		conf_file = os.path.join(self._hdpm._get_tmp_dir('conf'), fp)
		pickle.dump(conf, open(conf_file, 'w'))
		return conf_file

	def _get_streamer_command(self, module_path, encoded):
		path = module_path.split('.')
		module = '.'.join(path[:-1])
		class_name = path[-1]

		if encoded:
			return 'python -c "from %s import %s; %s()._run()"' % (module, class_name, class_name)
		else:
			return 'python', '-c', 'from %s import %s; %s()._run()' % (module, class_name, class_name)

	def _get_mapper_command(self, encoded=True):
		return self._get_streamer_command(self._mapper, encoded)

	def _get_reducer_command(self, encoded=True):
		if not self._reducer:
			return
		return self._get_streamer_command(self._reducer, encoded)

	def _get_combiner_command(self, encoded=True):
		if not self._combiner:
			return
		return self._get_streamer_command(self._combiner, encoded)

	def run_local(self):
		"""
		Run job in a local simulated environment
		"""

		import shutil

		env_files = self._hadoop_env.env_files

		env = {
			'PYTHONPATH': (os.pathsep.join([e[-1] for e in env_files])),
		}

		if self._conf_file:
			shutil.copy2(self._conf_file, os.path.basename(self._conf_file))
		if self._serialization_conf_file:
			shutil.copy2(self._serialization_conf_file, os.path.basename(self._serialization_conf_file))

		mapper = subprocess.Popen(self._get_mapper_command(False), env=env, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

		for path in self._input_paths:
			for line in open(path):
				mapper.stdin.write(line)
		mapper.stdin.close()

		out_stream = mapper.stdout.read()

		if self._combiner:
			combiner = subprocess.Popen(self._get_combiner_command(False), env=env, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

			for line in sorted(out_stream.split('\n')):
				combiner.stdin.write(line + '\n')
			combiner.stdin.close()

			out_stream = combiner.stdout.read()

		if self._reducer:
			reducer = subprocess.Popen(self._get_reducer_command(False), env=env, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

			for line in sorted(out_stream.split('\n')):
				reducer.stdin.write(line + '\n')
			reducer.stdin.close()

			out_stream = reducer.stdout.read()

		if self._conf_file:
			os.remove(os.path.basename(self._conf_file))
		if self._serialization_conf_file:
			os.remove(os.path.basename(self._serialization_conf_file))

		with open(self._output_path, 'w') as of:
			of.write(out_stream)

	def rm_output(self):
		"""
		Remove output dir
		"""

		try:
			self._hdpm.fs.rm(self._output_path)
		except self._hdpm.HadoopRunException:
			pass

	def cat_output(self):
		"""
		Returns a generator over mapreduce output
		"""

		from streamer import DEFAULT_OUTPUT_SERIALIZED
		output_serializer = (self._serialization_conf or {}).get('output', DEFAULT_OUTPUT_SERIALIZED)
		return self._hdpm.fs.cat(os.path.join(self._output_path, 'part-*'), serializer=output_serializer, tab_separated=True)

	def run(self):
		"""
		Run a mapreduce job
		"""

		env_files = self._hadoop_env.env_files

		cmd = ('jar', self._hdpm._hadoop_stream_jar)

		attrs = [
			('-mapper', self._get_mapper_command()),

			('-input', [path for path in self._input_paths]),
			('-output', self._output_path),

			('-cmdenv', 'PYTHONPATH=:%s' % (os.pathsep.join([e[0] for e in env_files]))),
			('-file', [efile[1] for efile in env_files]),

			('-reducer', self._get_reducer_command()),
			('-numReduceTasks', self._num_reducers),

			('-combiner', self._get_combiner_command()),

			('-file', self._conf_file),
			('-file', self._serialization_conf_file),
		]

		self._hdpm._run_hadoop_cmd_echo(cmd, attrs)
