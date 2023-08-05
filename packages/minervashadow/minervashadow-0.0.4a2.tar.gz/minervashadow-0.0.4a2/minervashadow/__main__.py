#!/usr/bin/env python
"""
Usage:
	minervashadow login
	minervashadow transcript
	minervashadow -h | --help
	minervashadow -v | --version

Examples:
	minervashadow login
	minervashadow transcript

Options:
	-h, --help     Show this screen.
	-v, --version  Print the current version.
"""

from minervashadow import get_version
from docopt import docopt
import ui.cli as cli
import minerva


def interruptable(fn):
	"""Exits the program if Ctrl+C is pressed"""
	def wrapper(*args, **kwargs):
		try:
			return fn(*args, **kwargs)
		except KeyboardInterrupt:
			print '\n\nExiting...\nHope to see you soon!'
			exit()
	return wrapper


@interruptable
def main():

	args = docopt(__doc__, version=get_version())

	credentials = cli.get_user_credentials()

	session = minerva.MinervaSession(credentials)

	print session.login()
	
	if not args['login']:
		print session.deal_with_request(args)

	session.logout()


if __name__ == '__main__':
	main()