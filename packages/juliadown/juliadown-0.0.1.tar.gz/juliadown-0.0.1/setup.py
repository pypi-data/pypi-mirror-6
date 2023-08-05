# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name = 'juliadown',
    version = '0.0.1',
    author = u'Thomas Levine',
    author_email = '_@thomaslevine.com',
    url = 'https://github.com/tlevine/juliadown',
    license = 'AGPL',
    packages = ['libjuliadown'],
    description = 'Parse hackpads from data dives into pretty JSON.',
#   long_description = open('readme.md').read(),
    install_requires = [line.strip() for line in open('requirements.txt')],
    scripts=['juliadown'],
)
