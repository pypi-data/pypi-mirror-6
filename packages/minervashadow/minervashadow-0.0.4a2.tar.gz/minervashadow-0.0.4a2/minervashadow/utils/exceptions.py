"""
Global minervashadow exception and warning classes.
"""

class MinervaException(Exception):
	"""A generic exception for minervashadow."""
	pass


class InvalidUsername(MinervaException):
	def __init__(self, username):
		self.username = username
	def __str__(self):
		return repr(self.username)


class NoInternetConnection(MinervaException):
	"""No internet connection has been detected."""
	def __str__(self):
		return 'No internet connection has been detected.'


class AuthenticationRequired(MinervaException):
	"""You need to login to minerva before accessing this info."""
	def __str__(self):
		return 'You need to login to minerva before accessing this info.'