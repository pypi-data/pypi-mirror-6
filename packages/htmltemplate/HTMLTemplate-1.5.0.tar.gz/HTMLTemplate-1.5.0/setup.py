try:
	from setuptools import setup
except:
	from distutils.core import setup

setup(name = 'HTMLTemplate',
	version = '1.5.0',
	description = 'HTML templating system.',
	author = 'HAS',
	author_email = '',
	url='http://py-templates.sourceforge.net',
	license = 'MIT',
	platforms = ['any'],
	long_description = 'HTMLTemplate converts HTML/XHTML templates into simple Python-based object models easily manipulated from ordinary Python code. Fast, powerful and easy to use.',
	py_modules = ['HTMLTemplate'],
	)