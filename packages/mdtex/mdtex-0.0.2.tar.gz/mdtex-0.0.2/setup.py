from setuptools import setup, find_packages

import os
long_description = 'Add a fallback short description here'
if os.path.exists('README.txt'):
	    long_description = open('README.txt').read()

setup(
		name = 'mdtex',
		version = '0.0.2',
		keywords = ('tex', 'latex', 'markdown', 'word'),
		description = '''
		This is a script for study, use M-V-C design patterns in Latex writing,
		it also can convert a part of markdown syntax to tex, but there are some bug in it
		''',
		license = 'MIT License',
		install_requires = [],

		author = 'Yufei-Li',
		author_email = 'sanguo0023@gmail.com',
		url = 'https://github.com/sanguo0023/mdtex',

		packages = find_packages(),
		package_data = {
			'mdtex': ['*.md', '*.pdf'],
		},
		platforms = 'any',
)
