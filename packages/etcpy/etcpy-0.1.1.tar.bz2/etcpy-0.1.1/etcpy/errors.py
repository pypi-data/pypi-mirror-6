#!/usr/bin/env python
"""Errors: Exceptions that can be returned by the etcd server 
"""

class EtcdError(Exception):
	def __repr__(self):
		name = self.__class__.__name__
		err_code = self.err_code
		msg = self.msg
		return "<{name}: {err_code} {msg}>".format(	name=name,
													msg=msg, 
													err_code=err_code)
	def __str__(self):
		err_code = self.err_code
		msg = self.msg
		return "{err_code} - {msg}".format(	msg=msg, 
											err_code=err_code)
# Command related errors
class EtcdKeyNotFound(EtcdError, KeyError):
	err_code = 100
	msg = "Key Not Found"
class EtcdTestFailed(EtcdError):
	err_code = 101
	msg = "Precondition/Test Failed" #test and set
class EtcdNotFileError(EtcdError, IOError):
	err_code = 102
	msg = "The specified key is not a File"
class EtcdMaxPeers(EtcdError):
	err_code = 103
	msg = "Max number of peers in the cluster has been reached"
class EtcdNotADir(EtcdError, OSError):
	err_code = 104
	msg = "The specified key is not a Directory"
class EtcdNodeExists(EtcdError):
	err_code = 105
	msg = "The requested key already exists" #create
class EtcdReservedKey(EtcdError):
	err_code = 106
	msg = "The prefix of given key is a keyword in etcd"

# Post form related errors
class EtcdPOSTError(EtcdError):
	pass
class EtcdValueRequired(EtcdPOSTError, ValueError):
	err_code = 200
	msg  = "Value is Required in POST"
class EtcdPrevValueRequired(EtcdPOSTError, ValueError):
	err_code = 201
	msg = "PrevValue is Required in POST"
class EtcdInvalidTTL(EtcdPOSTError, ValueError):
	err_code = 202
	msg = "The given TTL in POST is not a number"
class EtcdInvalidIndex(EtcdPOSTError, ValueError):
	err_code = 203
	msg = "The given index in POST is not a number"

# raft related errors
class EtcdRaftError(EtcdError):
	pass
class EtcdRaftInternalError(EtcdRaftError):
	err_code = 300
	msg = "Raft Internal Error"
class EtcdLeaderElectionError(EtcdRaftError):
	err_code = 301
	msg = "An Error occured during leader election"

# etcd related errors
class EtcdDaemonError(EtcdError):
	pass
class EtcdWatcherCleared(EtcdDaemonError):
	err_code = 400
	msg = "watcher has been cleared due to etcd recovery"
class EtcdEventIndexCleared(EtcdDaemonError):
	err_code = 401
	msg = "The event in requested index is outdated and has already been purged from stored history"


etcd_errors = {}
for key, value in locals().items():
	err_code = getattr(value, 'err_code', None)
	if err_code:
		etcd_errors[err_code] = value
del err_code
