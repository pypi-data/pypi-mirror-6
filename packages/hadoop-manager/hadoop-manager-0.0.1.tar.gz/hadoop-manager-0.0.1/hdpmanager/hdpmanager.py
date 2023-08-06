import os
import re
import shutil
import subprocess
import uuid

from hdpjob import HadoopJob
from hdpfs import HadoopFs

HADOOP_STREAMING_JAR_RE = re.compile(r'^hadoop.*streaming.*\.jar$')

# temporary dir are created in HDP_TMP_DIR
HDP_TMP_DIR = "/tmp/hadoop-manager"
# each temporary dir gets a randomly generated uuid suffix 
# example: /tmp/hadoop-manager/job-02e0d565-5924-419b-ae61-4ce3b56fd28b
HDP_DIR_PREFIX = "job"

class HadoopRunException(Exception):

	def __init__(self, msg, stderr=None):
		super(HadoopRunException, self).__init__(msg)
		self.stderr = stderr

	def __str__(self):
		err = super(HadoopRunException, self).__str__()
		if self.stderr:
			err += '\n' + self.stderr.read()
		return err

class HadoopManager(object):
	"""
	HadoopManager is a central object for managing hadoop jobs and hdfs

	In order to perform proper temporary directory cleanup use HadoopManager with 'with' statement.
	with HadoopManager(...) as manager:
		pass

	:param hadoop_home: home folder of hadoop package
	:param hadoop_fs_default_name: default hdfs home used when paths provided are relative
	:param hadoop_job_tracker: hadoop job tracker host:port
	"""

	HadoopRunException = HadoopRunException

	def __init__(self, hadoop_home, hadoop_fs_default_name=None, hadoop_job_tracker=None):
		tmp_directory = '%s_%s/' % (HDP_DIR_PREFIX, str(uuid.uuid4()))
		self._tmp_dir = os.path.join(HDP_TMP_DIR, tmp_directory)

		self._hadoop_home = hadoop_home
		self._hadoop_fs_default_name = hadoop_fs_default_name
		self._hadoop_job_tracker = hadoop_job_tracker

		self._hadoop_bin = self._find_hadoop_bin()
		self._hadoop_stream_jar = self._find_streaming_jar()

		self._fs = HadoopFs(self)

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self._rm_tmp_dir()

	@property
	def fs(self):
		"""
		HadoopFs object for managing hdfs
		"""
		return self._fs

	def create_job(self, input_paths, output_path, mapper, reducer=None, combiner=None, num_reducers=None, serialization=None, job_env=None, conf=None, root_package=None):
		"""
		Create HadoopJob object

		:param input_paths: list of input files for mapper
		:param output_path: path to the output dir
		:param mapper: import path to the mapper class
		:param reducer: import path to the reducer class
		:param combiner: import path to the combiner class
		:param root_package: import path to the subpackage in you app where the mapper/reducer/combiner import starts
		:param num_reducers: number of reducers
		:param conf: object that will be send to mapper, reducer and combiner. It will be accessible as self.conf in job objects.
		:param serialization: dict with configuration for input, output and internal serialization. Valid keys are input, output and inter, valid values are json, pickle and raw.
		:param job_env: dict which defines environment. Valid options are packages, package_data and requires. If packages aren't provided all packages returned by setuptools.find_packages in root_package will be included
		"""
		return HadoopJob(self, input_paths, output_path, mapper, reducer, combiner, num_reducers, serialization, job_env, conf, root_package)

	def _find_hadoop_bin(self):
		return '%s/bin/hadoop' % self._hadoop_home

	def _find_streaming_jar(self):
		paths = [os.path.join(self._hadoop_home, 'lib', 'hadoop-0.20-mapreduce', 'contrib'), # Try 4.0 path first
			self._hadoop_home]

		for path in paths:
			for (dirpath, _, filenames) in os.walk(path):
				for filename in filenames:
					if HADOOP_STREAMING_JAR_RE.match(filename):
						return os.path.join(dirpath, filename)
		return None

	def _get_cmd_list(self, t):
		if not t:
			return []

		cmd = None
		if isinstance(t, (tuple, list)):
			if len(t) > 1 and t[-1] is None:
				# Skip command if attr is None
				return []
			cmd = list(t)
		else:
			cmd = [t]

		if len(cmd) == 2 and isinstance(cmd[1], list):
			exploded = []
			for attr in cmd[1]:
				exploded += [cmd[0], attr]
			cmd = exploded

		return [str(c) for c in cmd]

	def _run_hadoop_cmd_echo(self, command, attrs):
		for line in self._run_hadoop_cmd(command, attrs):
			print line,
		print

	def _run_hadoop_cmd(self, command, attrs):
		cmd = [self._hadoop_bin]

		cmd += self._get_cmd_list(command)

		if self._hadoop_fs_default_name:
			cmd += ['-D', 'fs.defaultFS=%s' % self._hadoop_fs_default_name,]
		if self._hadoop_job_tracker:
			cmd += ['-D', 'mapred.job.tracker=%s' % self._hadoop_job_tracker,]

		if not isinstance(attrs, list):
			attrs = [attrs]
		for attr in attrs:
			cmd += self._get_cmd_list(attr)

		hadoop = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		for line in self._yield_lines(hadoop.stdout):
			yield line

		hadoop.wait()
		if hadoop.returncode != 0:
			raise HadoopRunException('Running hadoop command failed with code %s!' % hadoop.returncode, stderr=hadoop.stderr)

	def _yield_lines(self, pipe):
		while True:
			o = pipe.readline()
			if not o:
				break
			yield o

	def _get_tmp_dir(self, subdir=None):
		path = self._tmp_dir
		if subdir:
			path = os.path.join(path, subdir)
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def _rm_tmp_dir(self):
		if os.path.exists(self._tmp_dir):
			shutil.rmtree(self._tmp_dir,ignore_errors=True)
