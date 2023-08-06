from distutils.core import setup
from os.path import join, dirname
from setuptools import setup, find_packages
import pyegeg

setup(name='pyegeg',
	version=pyegeg.__version__,
	description='Library for analysis of electrogastroenterograms',
	long_description=open(join(dirname(__file__), 'README.rst')).read(),
	author='Aleksandr Popov, Aleksey Tyulpin',
	author_email='aleneus@gmail.com, alekseytyulpin@gmail.com',
	url='https://bitbucket.org/lex_t/pyegeg',
	keywords="electrogastroenterography electrogastrography python",
	packages=['pyegeg'],
	classifiers=(
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries',
	),
	license="GPL",
	install_requires=[
		'numpy',
		'scipy',
		'matplotlib',
	],
	platforms = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
)
