#! /usr/bin/env python
#-*- coding : utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

__author__  = 'TROUVERIE Joachim'
__version__ = '0.0.4'
__appname__ = 'Microbe'


from setuptools import setup, find_packages

requirements = []
for line in open('REQUIREMENTS.txt', 'r'):
    requirements.append(line)

setup(
    name = __appname__,
    version = __version__,
    packages = find_packages(),
    author = __author__,
    author_email = 'joachim.trouverie@joacodepel.tk',
    description = 'Micro Blog Engine inspired by Pelican and powered by Flask',
    long_description = open('README.md').read(),
    install_requires = requirements,
    include_package_data=True,
    url='http://joacodepel.tk/hg/microbe',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
    ],
    entry_points = {
        'console_scripts': [
            'microbe = microbe.views:main',
        ],
    },
)

