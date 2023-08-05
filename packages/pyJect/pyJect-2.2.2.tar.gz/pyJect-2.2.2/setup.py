try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

from versionup import get_version
version = get_version()


config = {
	'name': 'pyJect',
    'version': version,
	'author': 'Kyle Roux',
	'author_email': 'jstacoder@gmail.com',
	'description': 'a command line tool to make and orginize projects',
	'long_description': open('README','r').read(),
	'packages': ['pyject'],
    'py_modules': ['pyject'],
    'install_requires' : ['versionup'],
	'entry_points': {
		'console_scripts': [
			'pyject = pyject.main:main'
			]
		}
	}

setup(**config)

