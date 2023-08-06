__all__ = ['Mapper']

import sys
import traceback
import re

from streamer import Streamer

class Mapper(Streamer):

	def __init__(self, *args, **kwargs):
		super(Mapper, self).__init__(*args, **kwargs)

		self._line_grep = self.line_grep()

	def line_grep(self):
		"""
		Override this method to return a compiled regex, string or list of strings(matched with or) that each mapped line must match
		"""
		return None

	def _set_serializers(self, serializers):
		self._read_protocol = serializers['input']
		self._write_protocol = serializers['inter']

	def map(self, line):
		"""
		Override this methos for mapping the input line
		Output can be either returned or yielded as a key, value pair

		:param line: one line of the input file serialized by the input serializer
		"""
		return line

	def _grep_line(self, line):
		if not self._line_grep:
			return True

		if isinstance(self._line_grep, re._pattern_type):
			if not self._line_grep.search(line):
				return False
		elif isinstance(self._line_grep, list):
			if not any(string in line for string in self._line_grep):
				return False
		else:
			if not self._line_grep in line:
				return False

		return True

	def parse_line(self, line):
		if not self._grep_line(line):
			return

		return self._read_protocol.decode(line.rstrip())

	def parse_input(self):
		for line in self._input_stream:
			try:
				parsed_line = self.parse_line(line)
				if not parsed_line:
					continue
				self._out(self.map(parsed_line), enforce_tuple=False)
			except Exception, e:
				self.count('error lines', 1)
				sys.stderr.write('error %s processing line:\n%s\n' % (repr(e), repr(line)))
				traceback.print_exc(file=sys.stderr)

