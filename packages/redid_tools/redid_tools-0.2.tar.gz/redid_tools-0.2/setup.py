import os, codecs, re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# http://bugs.python.org/issue8876
del os.link

# pypanpoc is only needed for pypi setup, not for installing
try:
	import pypandoc
	desc = pypandoc.convert( 'README.md', 'rst' )
except Exception, e:
	desc = ''
	
# https://stackoverflow.com/questions/22604809/get-pip-setuptools-version-of-package-from-within-the-package/22652058?noredirect=1#comment34502193_22652058
def find_version(*file_paths):
	# Open in Latin-1 so that we avoid encoding errors.
	# Use codecs.open for Python 2 compatibility
	with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
		version_file = f.read()

		# The version line must have the form
		# __version__ = 'ver'
		version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
			version_file, re.M)
		if version_match:
			return version_match.group(1)
		raise RuntimeError("Unable to find version string.")
    
setup(
	name = 'redid_tools',
	packages = [ 'redid_tools' ],
	version = find_version('redid_tools','__init__.py'),
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
		'shelljob',
		'tabulate',
		'python-dateutil',
	],
	entry_points = {
		'console_scripts': [
			'redid = redid_tools.main:main',
			'redid-sync = redid_tools.sync:main',
		]
	},
)
