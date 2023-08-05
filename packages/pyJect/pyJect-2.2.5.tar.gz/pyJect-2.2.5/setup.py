try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

try:
    from versionup import get_version
except:
    def get_version():
        return '.'.join(open('.version','r').read())

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
    'requires' : ['versionup'],
	'entry_points': {
		'console_scripts': [
			'pyject = pyject.main:main'
			]
		}
	}

setup(**config)

