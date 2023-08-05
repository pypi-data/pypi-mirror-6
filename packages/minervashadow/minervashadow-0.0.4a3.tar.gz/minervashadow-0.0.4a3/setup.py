try:
	from setuptools import setup 
except:
	from disutils.core import setup

import minervashadow


dependencies=['docopt','mechanize','beautifulsoup4']

setup(

	name='minervashadow',
	version=minervashadow.get_version(),
	description='A python interface to the aging minerva website.',
	long_description=open('README.txt').read(),
	url='https://github.com/cadesalaberry/minervashadow',
	author='cadesalaberry',
	author_email='cadesalaberry@yahoo.com',
	install_requires=dependencies,
	packages=[
		'minervashadow','minervashadow.reader',
		'minervashadow.utils','minervashadow.ui'
		],
	entry_points={
		'console_scripts': [
			'minervashadow=minervashadow:main'
		],
	},
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Natural Language :: French',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6'
	]
)
