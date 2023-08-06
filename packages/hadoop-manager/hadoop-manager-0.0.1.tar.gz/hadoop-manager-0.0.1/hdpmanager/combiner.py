__all__ = ['Combiner']

from reducer import Reducer

class Combiner(Reducer):

	def reduce(self, key, values):
		"""
		Override this methos for reducing the input
		Output can be either returned or yielded as a key, value pair

		:param key: key returned by the mapper
		:param values: list of values retuned by the mapper
		"""
		return key, values

	def _set_serializers(self, serializers):
		self._read_protocol = serializers['inter']
		self._write_protocol = serializers['inter']
