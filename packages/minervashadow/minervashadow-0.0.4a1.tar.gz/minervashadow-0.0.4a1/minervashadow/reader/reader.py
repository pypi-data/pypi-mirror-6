from bs4 import BeautifulSoup
import login
import transcript

class MinervaReader:

	def __init__(self, site):
		self.site = site


	def login(self, html):

		"""
		Parses the result login page and extract the info message that determines a successful login.
		"""
		
		if not 'WELCOME' in html.geturl():
			return None, login.welcomeerr(html)
		else:
			return True, login.welcomemsg(html)


	def logout(self, html):
		"""
		Parses the content of the logout page and returns the message parsed.
		"""

		return 'You were successfully logged out.'


	def transcript(self, html, semester='all'):
		"""
		Parses the transcript page to extract the transcript as a json object.
		"""

		soup = BeautifulSoup(html)

		# Gets the div containing the table
		div = soup.body.find('div', {'class':'pagebodydiv'})

		# Gets the table inside that div
		tbl = div.find('table', {'class':'dataentrytable', 'width':'100%'})

		# Turns the html table into a list of lists (2D list)
		table = [col.findAll('td') for col in tbl.findAll('tr')]

		curriculum = transcript.get_curriculum(table)
		
		return curriculum