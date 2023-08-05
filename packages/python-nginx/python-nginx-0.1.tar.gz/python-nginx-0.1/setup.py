#!/usr/bin/env python

from distutils.core import setup

setup(
    name='python-nginx',
    version='0.1',
    description='Create and modify nginx serverblock configs in Python',
    author='Jacob Cook',
    author_email='jacob@jcook.cc',
    url='https://jcook.cc',
    packages=['nginx'],
    keywords = ['nginx', 'web servers', 'serverblock', 'server block'],
    download_url = 'https://github.com/jacook/python-nginx/archive/0.1.tar.gz',
    license = 'GPLv3',
    classifiers = [
    	"Development Status :: 3 - Alpha",
    	"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    	"Operating System :: Unix",
    	"Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ]
)
