import os
from setuptools import setup

# pypanpoc is only needed for pypi setup, not for installing
try:
	import pypandoc
	desc = pypandoc.convert( 'README.md', 'rst' )
except Exception, e:
	desc = ''
	
setup(
	name = 'redid_tools',
	packages = [ 'redid_tools' ],
	version = '0.1.2',
	description = 'Redid media distribituion network tools. Redid provides a media distribution network offering dynamic media transformations and signed resource access.',
	author = 'edA-qa mort-ora-y',
	author_email = 'eda-qa@disemia.com',
	url = 'https://pypi.python.org/pypi/redid_tools',
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python',
		'Intended Audience :: Developers',
		'Environment :: Console',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Multimedia :: Graphics',
		],
	long_description = desc,
	license = 'MIT',
	install_requires = [
		'requests',
		'pyyaml',
	],
	entry_points = {
		'console_scripts': [
			'redid = redid_tools.main:main',
		]
	},
)
