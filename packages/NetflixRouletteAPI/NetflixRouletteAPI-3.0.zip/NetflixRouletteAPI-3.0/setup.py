#!/usr/bin/env python

from setuptools import setup

setup(
    name='NetflixRouletteAPI',
    version='3.0',
    author='Andrew Sampson',
    author_email='andrew@codeusa523.org',
    license='GNU GENERAL PUBLIC LICENSE V3.0',
    url='http://netflixroulette.net/api/',
    keywords='netflix roulette webapi wrapper',
    description='The official python wrapper for the Netflix Roulette Web API',
    download_url="http://www.netflixroulette.net/api/downloads/NetflixRouletteAPI-3.0.zip",
    py_modules=["NetflixRoulette"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ]
)
