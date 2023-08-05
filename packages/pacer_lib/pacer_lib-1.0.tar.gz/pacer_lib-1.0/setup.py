from distutils.core import setup
setup(name='pacer_lib',
	  version='1.0',
	  author='C Zhang',
	  author_email='admin@uchicagolawandecon.org',
	  maintainer='Coase-Sandor Institute for Law and Economics',
	  url='http://www.uchicagolawandecon.org/research/tools/',
	  description='An interface for ',
	  long_description='Simple tool to facilitate searching, downloading and \
	  parsing documents from the PACER (Public Access to Court Electronic \
	  Records) database. (An existing PACER account is required). This is an updated\
      version of pacer-scraper-library and has been updated to be object-oriented.',
	  classifiers=['Development Status :: 4 - Beta', 
				  'Intended Audience :: Legal Industry', 
				  'Intended Audience :: Science/Research', 
				  'License :: Free To Use But Restricted', 
				  'Natural Language :: English',
				  'Programming Language :: Python :: 2.6',
				  'Topic :: Utilities'],
	  license = 'Python Software Foundation License',
	  py_modules=['scraper'],
	  requires = ['bs4', 'lxml', 'requests', 'datetime'],
	  )