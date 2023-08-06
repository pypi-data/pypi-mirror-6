from distutils.core import setup

setup(
	name = 'pgsql',
	py_modules = ['pgsql'],
	version = '1.1',
	description = 'A PostgreSQL database adapter for Python 3',
	long_description = open('README').read(),
	author = 'Antti Heinonen',
	author_email = 'heinoan@gmail.com',
	license = 'MIT',
	platforms = ['POSIX'],
	classifiers = [
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX',
		'Programming Language :: Python :: 3',
		'Topic :: Database',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
)
