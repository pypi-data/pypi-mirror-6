from minervashadow.utils import structures
import identify
import course
import re

def _clean_cell(cell):
		
	cell = cell.replace(u'\xa0', u'\n') # Removes weird characters
	cell = cell.replace(u'\xb2', u'')   # Removes the pow(2) character
	#cell = cell.strip().encode('utf8')	# Removes trailing spaces
	cell = ' '.join(cell.split())		# Removes useless '\n'

	return cell


def _clean_html_table(tbl):

	# Gets rid of the html formatting to get only text
	text_matrix = [[_clean_cell(cell.text) for cell in col] for col in tbl]

	# Gets rid of empty cells
	filtered = [[cell for cell in col if cell != ''] for col in text_matrix]
	
	# Gets rid of empty rows
	filtered = [col for col in filtered if col]
	
	return filtered


def _curriculum_from_clean_table(table):

	rows = iter(table)
	headers = [col for col in next(rows)]
	standing_headers = []

	curriculum = structures.minervaCurriculum()

	for line in table:
		l = len(line)

		if l == 1:
			if identify._is_semester_header(line):
				# Gets rid of the Readmitted word before the semester.
				title = re.sub('^Readmitted', '', line[0]).split(' ')
				sem = structures.minervaSemester(title[0],title[1])
				
				curriculum.addSemester(sem)

			elif identify._is_standing(line):
				curriculum.lastSemester().standing = re.sub('^Standing: ', '', line[0])

			elif identify._is_education(line):
				education = re.sub('^PREVIOUS EDUCATION ', '', line[0])
				curriculum.education = education

			elif identify._is_description(line):
				# Puts spaces before capital letters.
				description = re.sub('(\B[A-Z])', r' \1', line[0])
				curriculum.description = description
			else:
				#print l, 'Semester Name++', line
				pass

		elif l == 4:
			#print l, 'Exemption Ignored', line
			pass

		elif l == 5:
			if identify._is_standing_header(line):
				if not standing_headers:
					standing_headers = line
			else:
				# Credits transfer and course equivalence
				#print l, 'Unknown', line
				pass

		elif l == 6 or l == 7:
			_course = course.from_line(line)
			curriculum.lastSemester().addCourse(_course)

		elif l == 8:
			pass# print l, 'TERM GPA', line
		elif l == 9:
			pass# print l, 'CUM GPA', line
		elif l == 23:
			pass# print l, 'Advanced Standing', line

	return curriculum


def get_curriculum(table):

	table = _clean_html_table(table)

	return _curriculum_from_clean_table(table)
