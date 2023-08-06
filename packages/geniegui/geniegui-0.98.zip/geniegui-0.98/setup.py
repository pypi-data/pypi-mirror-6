from setuptools import setup

VERSION = open('VERSION.txt').read().strip()
README = open('README.md').read()
AUTHOR = 'Sven Rahmann'
EMAIL = 'Sven.Rahmann@gmail.com'
URL = 'https://bitbucket.org/svenrahmann/geniegui/'
LICENSE = 'MIT'

CLASSIFIERS=[
'Development Status :: 5 - Production/Stable',
'Intended Audience :: Developers',
'Intended Audience :: Science/Research',
'Natural Language :: English',
'License :: OSI Approved :: MIT License',
'Operating System :: OS Independent',
'Programming Language :: Python',
'Programming Language :: Python :: 3',
'Programming Language :: Python :: 3.2',
'Programming Language :: Python :: 3.3',
'Programming Language :: Python :: 3.4',
'Topic :: Scientific/Engineering',
#'Topic :: Desktop Environment',
]


setup(
    name = 'geniegui',
    description = 'generate and run a GUI from an argparse.ArgumentParser object of a console application',
    py_modules = ['geniegui'],
    version = VERSION, 
    author = AUTHOR,
    author_email = EMAIL,
    url = URL,
    long_description = README,
    license = LICENSE,
    classifiers = CLASSIFIERS,
)
