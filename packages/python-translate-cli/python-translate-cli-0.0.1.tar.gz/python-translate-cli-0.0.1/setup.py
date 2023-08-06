#!/usr/bin/env python3
#-*-coding: utf8 -*-
from setuptools import setup, find_packages

setup(
    name='python-translate-cli',
    version='0.0.1',
    description='命令行查词',
    long_description='简易终端查词工具',
    author='mapleray',
    url='http://sillymind.me',
    author_email='zhiwuliao@gmail.com',
    license='GPL',
    keywords=('google', 'python', 'cli', 'dictionary', 'terminal'),
    classifiers = '',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    zip_safe = False,
    platforms = 'any',
    include_package_data = True,
    install_requires = [
        'requests',
    ],
    entry_points = {
        'console_scripts': [
            'tl = python_translate_cli.cli:main'
        ]
    },
)
