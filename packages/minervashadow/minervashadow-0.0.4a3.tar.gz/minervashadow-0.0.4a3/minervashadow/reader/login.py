from HTMLParser import HTMLParser
import urlparse

def welcomemsg(html):
	query = urlparse.parse_qs(html.geturl())
	messg = HTMLParser().unescape(query['msg'][0])
	messg = messg.replace('<b>', '').replace('WELCOME ', '')
	return messg.split('</b>')

def welcomeerr(html):
	# TODO:Instead we should try reading the error message displayed on the html
	return ['Authorization Failure - you have entered an invalid McGill Username / Password.']