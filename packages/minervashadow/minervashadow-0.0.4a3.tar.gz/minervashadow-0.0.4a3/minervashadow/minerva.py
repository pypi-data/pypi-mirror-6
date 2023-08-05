from utils import exceptions as ex
import utils.structures as structures
from reader import reader
import writer
import urllib2


def internet_required(fn):
	def wrapper(*args, **kwargs):
		try:
			return fn(*args, **kwargs)
		except urllib2.URLError:
			raise ex.NoInternetConnection
	return wrapper


def login_required(fn):
	def wrapper(self, *args, **kwargs):
		if not self.user.loggedin:
			raise ex.AuthenticationRequired
		return fn(self, *args, **kwargs)
	return wrapper


class MinervaSession:

	def __init__(self, user):

		self.site = structures.minervaSite()
		self.user = structures.minervaCred(user[0],user[1])
		self.writer = writer.MinervaWriter(self.site)
		self.reader = reader.MinervaReader(self.site)


	@internet_required
	def login(self) :

		# Logs in, This page can confirm a succesful login.
		loginResponse = self.writer.login(self.user)

		loggedin, msg = self.reader.login(loginResponse)

		self.user.loggedin = loggedin

		return msg[0]


	@internet_required
	def logout(self):
		
		if not self.user.loggedin:
			message = 'You are already logged out.'
		else:
			# Logs out.
			logoutPage = self.writer.logout()
			message = self.reader.logout(logoutPage)
		
		return message


	@internet_required
	@login_required
	def transcript(self):

		transcriptPage = self.writer.transcript()
		
		curriculum = self.reader.transcript(transcriptPage)

		return curriculum


	@internet_required
	def deal_with_request(self, req):

		response = ''

		if req['login']:
			response = self.login()

		elif req['transcript']:
			response = self.transcript()

		else:
			response = 'Not implemented yet.'

		return response