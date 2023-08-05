# shelljob setup.py
import os
from setuptools import setup

# https://bugs.launchpad.net/mortoray.com/+bug/1274176
try:
	import pypandoc
	desc = pypandoc.convert( 'README.md', 'rst' )
except Exception, e:
	desc = ''

def list_files(path):
	m = []
	for root, dirnames, filenames in os.walk(path):
		for filename in filenames:
			m.append(os.path.join(root, filename))
	return m
			
setup(
	name = 'shelljob',
	packages = [ 'shelljob' ],
	version = '0.4.2',
	description = 'Run multiple subprocesses asynchronous/in parallel with streamed output/non-blocking reading. Also various tools to replace shell scripts.',
	author = 'edA-qa mort-ora-y',
	author_email = 'eda-qa@disemia.com',
	url = 'https://pypi.python.org/pypi/shelljob',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Programming Language :: Python',
		'Intended Audience :: Developers',
		'Environment :: Console',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Operating System :: OS Independent',
		'Topic :: Terminals',
		'Topic :: System',
		'Topic :: Software Development :: Build Tools',
		],
	long_description = desc,
	package_data = { 'shelljob': [ 'doc/*' ] },
	license = 'GPLv3',
)
