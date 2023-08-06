# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


_VERSION = '0.1'

def get_version():
    return _VERSION

setup(
    name='albumthief',
    license='GPLv2',
    description='Very fast album downloader made using gevent. ',
    author='Chaobin Tang',
    author_email='cbtchn@gmail.com',
    url='https://github.com/chaobin/albumthief',
    version=get_version(),
    classifiers=[
        'Programming Language :: Python :: 2.6',
    ],
    packages = ['albumthief',],
    install_requires=[
        'gevent',
        'BeautifulSoup',
        'requests'
    ],
    entry_points = {
        'console_scripts': [
            'steal-album = albumthief.manage:main'
        ]
    }
)