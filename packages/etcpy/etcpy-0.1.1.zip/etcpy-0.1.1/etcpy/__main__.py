#!/usr/bin/env python
"""etcpy: Interface to etcd for python"""

__author__ = "Da_Blitz"
__email__ = "code@pocketnix.org"
__url__ = "http://code.pocketnix.org"
__version__ = "0.1.1" # AUTOBUMP_VERSION: __version__ = "{version}"
__license__ = "BSD 3 Clause"


from collections import namedtuple
from json import loads
import requests
import logging
import errors
import sys

log = logging.getLogger("etcpy")

EtcdDir = namedtuple('EtcdDir', 'key nodes modified_index created_index ttl expiration')
class EtcdDir(EtcdDir):
	"""Represents a result back from an Etcd server for a node representing a directory (eg a GET)
	
	:param str key: The key this object represents
	:param EtcdValue nodes: A list of :py:class:`EtcdDir` and :py:class:`EtcdValue` objects representing the contents of the directory
	:param int modified_index: The modifiedIndex filed returned by the server
	:param int created_index: The createdIndex field returned by the server
	:param int ttl: If not None, the amount of seconds until this key expires
	:param str expiration: The time that this key will expire
	"""
	__slots__ = []
	dir = True
	def __len__(self):
		return len(self.nodes)

	def __iter__(self):
		return iter(self.nodes)
		
EtcdValue = namedtuple('EtcdValue', 'key value modified_index created_index ttl expiration prev_value')
class EtcdValue(EtcdValue):
	"""Represents a value stored on the server
	
	:param str key: The key this object represents
	:param value: The raw value stored on the server
	:param int modified_index: The modifiedIndex filed returned by the server
	:param int created_index: The createdIndex field returned by the server
	:param int ttl: If not None, the amount of seconds until this key expires
	:param str expiration: The time that this key will expire
	"""
	__slots__ = []
	dir = False
	# TODO: Add JSON convince function

class Etcd(object):
	"""Represents an Etcd cluster with which operations can be performed against"""
	def __init__(self, addr, port=4001, client_cert=None, server_ca=None, secure=True):
		""" 		
		:param str addr: The address of the etcd server to connect to
		:param int port: The port of the Server to connect to (defaults to 4001)
		:param client_cert: The User certificate to prevent to the server to authenticate with
		:param server_ca: The CA to verify the server supplied certificate against
		:param bool secure: Should the connection be made with https
		"""
		self.api_version = "v2"
		self.addr = addr
		self.port = port
		self.client_cert = client_cert
		self.server_ca = server_ca

		if client_cert or server_ca or secure:
			url = "https://"
		else:
			url = "http://"
			
		url += addr
		url += ":{}".format(port)

		url += "/{}".format(self.api_version)
		
		self.base_url = url
		
		self.keys_url = url + "/keys"

	
	def _request(self, key, data=None, query_args={}, action=requests.get):
		"""Convinence function to help move all commn code to a central location
		
		:param str key: The Key to make the request against
		:param dict data: The form data to be sent to the server
		:param dict query_args: a dictonary of query args to be appended to the url
		:param action: A :py:class:`requests.Request` subclass to select the HTTP VERB type
		"""
		# TODO:
		# * Add client auth via ssl
		# * Add server cert verification
		url = self.keys_url + str(key)
		query_args = make_query_string(query_args)
		url = url + query_args

		resp = action(url, data=data)

		if not resp.ok:
			if resp.status_code == 404:
				etcd_error = errors.EtcdKeyNotFound()	
			else:
				etcd_code = resp.json()['errorCode']
				etcd_error = errors.etcd_errors[etcd_code]()
			log.debug('Operation on %s returned an error %s', key, etcd_error)
			raise etcd_error
		
		node = resp.json()['node']
		
		return self._convert_to_etcd_value(node)
	
	@classmethod
	def _convert_to_etcd_value(cls, node):
		"""Recursive convert a node of tree of nodes to thier respective types"""
		key = node['key'] # regenerate key as a POST may have selected one for us
		modified_index = node.get('modifiedIndex') # Root node is RO and never modified
		created_index = node.get('createdIndex') # Root node is RO and never created
		ttl = node.get('ttl')
		expiration = node.get('expiration')
		prev_value = node.get('prevValue')

		if node.get('dir', False):
			nodes = node.get('nodes', [])
			nodes = [cls._convert_to_etcd_value(x) for x in nodes]
			ret_val = EtcdDir(key, nodes, modified_index, created_index, ttl, expiration)
		else:
			value = node.get('value')
			ret_val = EtcdValue(key, value, modified_index, created_index, ttl, expiration, prev_value)

		return ret_val
	
	def get(self, key, recursive=False, wait=None, index=None):
		"""Retrive a value from etcd
		
		:param str key: The key to lookup
		:param bool recursive: Retrive the specified key and all its subkeys (dir only)
		:param bool wait: Wait for a change on the specified key (can be used with recursive)
		:param int index: If supplied along with wait=True, return/wait on changes since the index specified and not the latest value
		"""
		options = {}
		if recursive:
			options['recursive'] = "true"
		if wait:
			options['wait'] = "true"
			if index:
				options['waitIndex'] = index

		log.debug('GET: %s', key)

		resp = self._request(key, query_args=options)
		
		return resp

	def set(self, key, val, ttl=None, dir=False, old_value=None, old_index=None, exists=None):
		"""Set a value in etcd
		
		:param str key: The key to set
		:param val: The value to set
		:param int ttl: The expiry time (in seconds) of the newly created entry
		:param bool dir: Should a directory be created
		:param old_value: The old value for compare and swap operations
		:param int old_index: The old index for compare and swap operations
		:param bool exists: Should the key be created if it previously exists? use None for "Do not care"
		"""
		options = {}
		if ttl:
			options['ttl'] = ttl
		if dir:
			options['dir'] = 'true'
		if old_value is not None:
			options['prevValue'] = old_value
		if old_index is not None:
			options['prevIndex'] = old_index
		if exists is not None:
			options['prevExist'] = "true" if exists else "false"

		log.debug('SET: %s', key)

		data = {'value':val}

		resp = self._request(key, data, options, requests.put)

		return resp

	def delete(self, key, dir=False, recursive=False):
		"""Delete a key from etcd
		
		:param str key: The key to delete
		:param bool dir: Must be set to True to delete directories
		:param bool recursive: Recursively delete keys under the specified directory
		"""
		options = {}
		if dir:
			options['dir'] = "true"
		if recursive:
			options['recursive'] = "true"
		
		log.debug('DEL: %s', key)
		
		resp = self._request(key, query_args=options, action=requests.delete)
		
		return resp

	__getitem__ = get
	__setitem__ = set
	__delitem__ = delete

	def auto_create(self, key, val, dir=False, ttl=None):
		"""Create a key in a directory and let etcd handle name generation
		
		can be handy to avoid race conditions when creatign key names client side
		The generated keys are unique and will not be in conflict with each other
		
		:param str key: The directory to create the key in
		:param val: The value to be written to the key
		:param bool dir: Should the created key be a directory
		:param int ttl: The expiry time (in seconds) of the newly created entry
		"""
		options = {}
		if ttl:
			options['ttl'] = ttl
		if dir:
			options['dir'] = 'true'

		log.debug('POST: %s', key)

		data = {'value':val}

		resp = self._request(key, data, options, requests.post)

		return resp
				
	def update(self, key, val, ttl=None, dir=False, old_value=None, old_index=None):
		"""Only update a value, do not create it if it does not exist
		
		This is a convience function around :py:meth:`Etcd.set`

		:param str key: The key to set
		:param val: The value to set
		:param int ttl: The expiry time (in seconds) of the newly created entry
		:param bool dir: Should a directory be created
		:param old_value: The old value for compare and swap operations
		:param int old_index: The old index for compare and swap operations
		"""
		return self.set(key, val, ttl, dir, old_value, old_index, exists=True)
		
	def create(self, key, val, ttl=None, dir=False, old_value=None, old_index=None):
		"""Only create a key if it did not previously exist
		
		This is a convience function around :py:meth:`Etcd.set`

		:param str key: The key to set
		:param val: The value to set
		:param int ttl: The expiry time (in seconds) of the newly created entry
		:param bool dir: Should a directory be created
		:param old_value: The old value for compare and swap operations
		:param int old_index: The old index for compare and swap operations
		"""
		return self.set(key, val, ttl, dir, old_value, old_index, exists=False)

	def make_dir(self, key, ttl=None):
		"""Make a directory
		
		This is a convience function around :py:meth:`Etcd.set`

		:param str key: The directory to create the key in
		:param int ttl: The expiry time (in seconds) of the newly created entry
		"""
		return self.set(key, None, ttl=ttl, dir=True)

	def watch(self, key, recursive=False, index=None):
		"""Block and Watch a file or directory for changes
		
		This is a convience function around :py:meth:`Etcd.get`

		Returns the change that was made
		
		:param str key: The directory to create the key in
		:param bool recursive: Retrive the specified key and all its subkeys (dir only)
		:param int index: If supplied along with wait=True, return/wait on changes since the index specified and not the latest value
		"""
		return self.get(key, recursive=recursive, wait=True, index=index)


def join(start, *path):
	"""Join 2 or more path components, if any component begins with '/', this will 
	discard input up to that point and replace it with the tokens from that point forward
	
	>>> join('temp1', 'temp2')
	'temp1/temp2'

	>>> join('temp1', '/temp2')
	'/temp2'
	
	"""
	SEP = "/"
	
	output = [start]
	for fragment in path:
		if fragment.startswith(SEP):
			output = ["", fragment[1:]]
		else:
			output.append(fragment)
	
	return SEP.join(output)

def make_query_string(vals):
	"""Take a dictonary of query string values and convert them to a string for appending to a url
	
	:param dict vals: The dict of values to be converted
	:returns: string to append to the url
	"""
	new_vals = []
	for key, val in vals.iteritems():
		val = str(val)
		new_vals.append("=".join((key, val)))
	
	vals = "&".join(new_vals)
	
	return "?" + vals
		

def main():
	from argparse import ArgumentParser
	args = ArgumentParser()
	args.add_argument("server_address", help="IP Address of the etcd server (IP[:PORT])")
	
	options = args.parse_args()
	
	addr = options.server_address.split(":") + ["4001"]
	addr, port = addr[:2]
	try:
		port = int(port)
	except ValueError:
		sys.stderr.write('Supplied port is not a valid integer: "{}"\n'.format(port))
		sys.exit(1)

	print addr, port

	s = Etcd(addr, port)
	print "Machines:"
	print s.machines
	print
	print "Leader:"
	print s.leader

	
if __name__ == "__main__":
	main()
