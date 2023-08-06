from setuptools import setup, find_packages

VERSION = open('VERSION.txt').read().strip()
README = open('README.txt').read()
AUTHOR = 'Sven Rahmann'
EMAIL = 'Sven.Rahmann@gmail.com'
URL = 'https://bitbucket.org/svenrahmann/amplikyzer/'
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
    name = 'amplikyzer',
    description = 'an amplicon methylation analyzer for flowgrams (SFF files)',
    scripts = ['bin/show-nonascii.py', 'bin/amplikyzer', 'bin/amplikyzergui'],
    install_requires=['geniegui >= 0.96', 'mamaslemonpy >=0.96'],
    packages = find_packages(),
    version = VERSION, 
    author = AUTHOR,
    author_email = EMAIL,
    url = URL,
    long_description = README,
    license = LICENSE,
    classifiers = CLASSIFIERS,
)

