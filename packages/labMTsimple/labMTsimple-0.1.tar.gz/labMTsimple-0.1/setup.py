from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name = 'labMTsimple',
    packages = ['labMTsimple'],
    version = '0.1',
    description = 'Basic usage script for LabMT1.0 dataset',
    long_description = long_description,
    author = 'Andy Reagan',
    author_email = 'andy@andyreagan.com',
    url = 'https://github.com/andyreagan/labMT-simple', 
    download_url = 'https://github.com/andyreagan/labMT-simple/tarball/0.1',
    keywords = [],
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python'],
    )
