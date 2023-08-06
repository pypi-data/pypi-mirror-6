from protocol import get_protocol_from_name

class HadoopFs(object):

	def __init__(self, hadoop_manager):
		self._hdpm = hadoop_manager

	def cat(self, path, serializer='raw', tab_separated=False):
		"""
		Returns a generator over files defined by path

		:param path: path to the files
		:param serializer: input serializer. Options are json, pickle and raw(default)
		:param tab_seperated: boolean if input is tab separated
		"""
		output = self._hdpm._run_hadoop_cmd('fs', ('-cat', path))
		output_serializer = get_protocol_from_name(serializer)

		for line in output:
			line = line.rstrip()

			if tab_separated:
				ls = line.split('\t')
				if len(ls) > 1:
					yield tuple(output_serializer.decode(part) for part in line.split('\t'))
				else:
					yield output_serializer.decode(line)
			else:
				yield output_serializer.decode(line)

	def rm(self, path):
		"""
		Recursively remove all files on the path

		:param path: path to the files
		"""
		self._hdpm._run_hadoop_cmd_echo('fs', ('-rm', '-r', path))
