from setuptools import setup, find_packages

VERSION = open('VERSION.txt').read().strip()
README = open('README.txt').read()
AUTHOR = 'Sven Rahmann'
EMAIL = 'Sven.Rahmann@gmail.com'
URL = 'https://bitbucket.org/svenrahmann/mamaslemonpy/'
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
'Topic :: Scientific/Engineering :: Bio-Informatics',
]


setup(
    name = 'mamaslemonpy',
    description = 'index biological sequences and run maximial matches queries on them',
    #py_modules = ['geniegui'],
    packages = find_packages(),
    version = VERSION, 
    author = AUTHOR,
    author_email = EMAIL,
    url = URL,
    long_description = README,
    license = LICENSE,
    classifiers = CLASSIFIERS,
)

