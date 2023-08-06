try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name = 'gcjio',
	description = 'Input parser & output formatter for Google Code Jam problems',
	version = '1.7',

	author = 'Kye W. Shi',
	author_email = 'shi.kye@gmail.com',

	install_requires = [],
	packages = ['gcjio'],
	scripts = []
)
