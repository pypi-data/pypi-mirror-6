import re

def _is_semester_header(line):
	sem_header_regex = re.compile('^(Readmitted|)(Fall|Winter|Summer) ([0-9]{4})$')
	return not not sem_header_regex.match(line[0])

def _is_standing(line):
	return line[0].startswith('Standing: ')

def _is_education(line):
	return line[0].startswith('PREVIOUS EDUCATION ')

def _is_description(line):
	return line[0].startswith('Bachelor of ')

def _is_standing_header(line):
	return line[0] == 'Advanced Standing& Transfer Credits:'

def _is_a_grade(text):
	rule = '^([A-C][+-]?|D|F'
	rule += '|HH|IP|JK|KE|K\*|KF|KK|LL|LE|L\*'
	rule += '|NA|&&|NE|NR|P|Q|R|S|U|W|WF|WL|W--|--)$'
	grade_regex = re.compile(rule)
	return not not grade_regex.match(text)

if __name__ == '__main__':
	print 'B+', _is_a_grade(u'B+')
	print 'K*', _is_a_grade(u'K*')
	print '3',  _is_a_grade(u'3')