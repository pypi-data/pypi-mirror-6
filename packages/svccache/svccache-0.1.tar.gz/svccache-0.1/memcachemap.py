"""
A memcache wrapper with a mapping interface.

Except keys() which is not supported by memcache (raises
a NotImplementedError).

Requires memcache module and memcached ready to run.

>>> import time
>>> sock = '/tmp/test.sock'
>>> p = _spawn_memcached(sock)
>>> m = MemcacheMap(['unix:' + sock])
>>> m['key'] = 'value'
>>> m['key']
'value'
>>> del m['key']
>>> m['key']
Traceback (most recent call last):
	...
KeyError: 'key'
>>> m.keys()
Traceback (most recent call last):
	...
NotImplementedError
>>> p.terminate()
"""

import time
import memcache

class MemcacheMap(object):
	def __init__(self, *args):
		self._client = memcache.Client(*args)

	def __getitem__(self, k):
		value = self._client.get(k)
		if value is None:
			raise KeyError(k)
		return value

	def __setitem__(self, k, v):
		if not self._client.set(k, v):
			raise MemcacheMapError('Could not put ' + k)

	def __delitem__(self, k):
		self._client.delete(k)

	def keys(self):
		raise NotImplementedError


import subprocess

def _spawn_memcached(sock):
	"""Helper function for tests. Spawns a memcached process attached to sock.
	Returns Popen instance. Terminate with p.terminate().
	Note: sock parameter is not checked, and command is executed as shell.
	Use only if you trust that sock parameter. You've been warned.
	"""
	p = subprocess.Popen('memcached -s ' + sock, shell=True)
	time.sleep(0.2) # memcached needs to initialize
	assert p.poll() is None # make sure it's running
	return p

class MemcacheMapError(Exception):
	pass
