class Component(object):

	def __init__(self, *interfaces, **named_interfaces):
		self._interfaces = named_interfaces
		for interface in interfaces:
			self._interfaces[interface.get_name()] = interface

	def put_interface(self, interface):
		interface = self._interfaces[interface.get_name()]
		self._interfaces[interface.get_name()] = interface
		return interface

	def get_interface(self, name):
		return self._interfaces[name]

	def get_interfaces(self):
		return self._interfaces.values()

class Interface(object):

	def __init__(self, name, is_client = True):
		self._name = name
		self._is_client = is_client

	def get_name(self):
		return self._name

	def is_client(self):
		return self.is_client