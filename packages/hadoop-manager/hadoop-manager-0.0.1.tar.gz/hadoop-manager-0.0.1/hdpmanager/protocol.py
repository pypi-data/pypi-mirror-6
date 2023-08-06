import cPickle as pickle

try:
	try:
		import ujson as json
	except ImportError:
		import simplejson as json
except ImportError:
	import json


class _CachingProtocol(object):

	_cached_values = None

	def __init__(self):
		self._cached_values = {}

	def _loads(self, v):
		raise NotImplementedError

	def _dumps(self, v):
		raise NotImplementedError

	def encode(self, o, cache_idx=-1):
		if cache_idx < 0:
			return self._dumps(o)

		cached_value = self._cached_values.get(cache_idx)
		if cached_value and cached_value[0] == o:
			return cached_value[1]

		dumps = self._dumps(o)
		self._cached_values[cache_idx] = (o, dumps)

		return dumps

	def decode(self, s, cache_idx=-1):
		if cache_idx < 0:
			return self._loads(s)

		cached_value = self._cached_values.get(cache_idx)
		if cached_value and cached_value[1] == s:
			return cached_value[0]

		loads = self._loads(s)
		self._cached_values[cache_idx] = (loads, s)

		return loads


class PickleProtocol(_CachingProtocol):

	_TRAILING_CHARS = '\n.' # All pickle strings end with these

	def _dumps(self, o):
		return pickle.dumps(o).rsplit(self._TRAILING_CHARS)[0].encode('string_escape')

	def _loads(self, s):
		return pickle.loads(s.decode('string_escape') + self._TRAILING_CHARS)

class JsonProtocol(_CachingProtocol):

	def _dumps(self, o):
		return json.dumps(o)

	def _loads(self, s):
		return json.loads(s)

class RawProtocol(object):

	def encode(self, o, cache_idx=-1):
		return o

	def decode(self, s, cache_idx=-1):
		return s

def get_protocol_from_name(name):
	return {
		'json' : JsonProtocol,
		'pickle': PickleProtocol,
		'raw': RawProtocol,
	}[name]()
