import minervashadow.utils.structures as structures
import identify


def _course_missing_avg(line):
	if len(line) < 8:
		return not identify._is_a_grade(line[-1])
	else:
		return False


def _course_missing_remarks(line):
	if 5 < len(line) and len(line) < 8:
		if identify._is_a_grade(line[-1]) and line[-2].isdigit():
			return True
	else:
		return False


def _course_missing_credits(line):
	if 5 < len(line) and len(line) < 8:
		for field in line[5:]:
			if field.isdigit():
				return False
		return True
	return False


def _is_valid(line):

	# Checks if the size has been fixed
	if not len(line) is 8:
		return False
	
	# Checks if the grade field is actually a grade
	if not identify._is_a_grade(line[4]):
		return False

	#Checks if the earned field has been fixed
	if not line[6].isdigit():
		return False

	# Checks the the average is a valid grade, and not blank
	if not identify._is_a_grade(line[7]):
		return False

	return True


def _fix(line):

	_fixed_line = list(line)

	if _course_missing_avg(line):
		_fixed_line.append('--')
		
	if _course_missing_credits(line):
		_fixed_line.insert(-1, u'0')
		
	if _course_missing_remarks(_fixed_line):
		_fixed_line.insert(-2, u'')
		
	return _fixed_line


def from_line(line):

	_course = structures.minervaCourse(line[0])
	
	if not _is_valid(line):
		fixed_line = _fix(line)
	else:
		fixed_line = list(line)

	if _is_valid(fixed_line):
		_course.number	= fixed_line[1]
		_course.title	= fixed_line[2]
		_course.credits	= fixed_line[3]
		_course.grade	= fixed_line[4]
		_course.remarks	= fixed_line[5]
		_course.earned	= fixed_line[6]
		_course.average = fixed_line[7]
	else:
		print line
		print 'in :', len(line), line[0], line[5:]
		print 'out:', len(fixed_line), line[0], fixed_line[5:]
		return structures.minervaCourse('Empty')
	
	return _course