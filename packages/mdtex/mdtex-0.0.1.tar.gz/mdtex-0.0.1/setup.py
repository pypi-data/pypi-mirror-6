from setuptools import setup, find_packages

setup(
		name = 'mdtex',
		version = '0.0.1',
		keywords = ('tex', 'latex', 'markdown', 'word'),
		description = '''
		This is a script for study, use M-V-C design patterns in Latex writing,
		it also can convert a part of markdown syntax to tex, but there are some bug in it
		''',
		license = 'MIT License',
		install_requires = [],

		author = 'Yufei-Li',
		author_email = 'sanguo0023@gmail.com',

		packages = find_packages(),
		platforms = 'any',
)
