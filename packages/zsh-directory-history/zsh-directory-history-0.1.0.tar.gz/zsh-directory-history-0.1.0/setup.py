# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='zsh-directory-history',
    version='0.1.0',
    author='Timm Schäuble',
    author_email='tymmm1@gmail.com',
    scripts=['dirhist','dirlog'],
    url='https://github.com/tymm/directory-history',
    description='Scripts needed to use my directory-history plugin for zsh.',
    long_description=open('README.txt').read(),
)
