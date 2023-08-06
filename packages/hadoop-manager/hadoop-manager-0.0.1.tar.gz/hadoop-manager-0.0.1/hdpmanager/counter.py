import os
import sys
import collections
import atexit

FLUSH_INTERVAL_FILE = 1000
FLUSH_INTERVAL_TERMINAL = 10

COMMA_REPLACE_CHARACTER = ';'


class Counter(object):

	def __init__(self, group='hdp'):
		self._counters = collections.defaultdict(int)

		self._group = group

		# stderr is not a file in Jenkins
		self._is_terminal = isinstance(sys.stderr, file) and os.isatty(sys.stderr.fileno())
		if self._is_terminal:
			self._flush_interval = FLUSH_INTERVAL_TERMINAL
			atexit.register(self._flush_terminal, clear=False)
		else:
			self._flush_interval = FLUSH_INTERVAL_FILE
			atexit.register(self._flush_file)

	def _flush_file(self, counter=None, clear=True):
		if counter is None:
			for counter in self._counters.iterkeys():
				self._flush_file(counter)
			return

		if self._counters[counter] > 0:
			name = counter.replace(',', COMMA_REPLACE_CHARACTER)
			sys.stderr.write('reporter:counter:%s,%s,%s\n' % (self._group, name, self._counters[counter]))
			self._counters[counter] = 0

	def _flush_terminal(self, counter=None, clear=True):
		for counter in self._counters.iterkeys():
			name = counter.replace(',', COMMA_REPLACE_CHARACTER)
			sys.stderr.write('counter:%s,%s,%s\n' % (self._group, name, self._counters[counter]))
		if clear:
			sys.stderr.write('\033[%dA' % (len(self._counters) + 1))

	def count(self, counter, amount=1):
		current_value = self._counters[counter]
		new_value = current_value + amount
		self._counters[counter] = new_value
		if new_value / self._flush_interval > current_value / self._flush_interval:
			if self._is_terminal:
				self._flush_terminal(counter, clear=False)
			else:
				self._flush_file(counter)
