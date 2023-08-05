import os


def get_pkg_data(name, directory):
	"""
	Compile the list of packages available, because distutils doesn't have
	an easy way to do this (Taken from Django setup.py).
	"""
	packages, package_data = [], {}

	root_dir = os.path.dirname(directory)
	if root_dir != '':
		os.chdir(root_dir)
	package_dir = name

	for dirpath, dirnames, filenames in os.walk(package_dir):
		# Ignore PEP 3147 cache dirs and those whose names start with '.'
		dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
		parts = fullsplit(dirpath)
		package_name = '.'.join(parts)
		if '__init__.py' in filenames and is_package(package_name):
			packages.append(package_name)
		elif filenames:
			relative_path = []
			while '.'.join(parts) not in packages:
				relative_path.append(parts.pop())
			relative_path.reverse()
			path = os.path.join(*relative_path)
			package_files = package_data.setdefault('.'.join(parts), [])
			package_files.extend([os.path.join(path, f) for f in filenames])

	return packages, package_data


if __name__ == '__main__':
	
	print os.path.dirname(__file__)

	p, d = get_pkg_data(name='minervashadow',
		directory='/home/cadesalaberry/Apps/minervashadow/'
	)
	print p

	print '\n\n', d
