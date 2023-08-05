#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup


setup(
    name='resellerclub',
    url='https://github.com/miracle2k/resellerclub-python',
    version='0.1.3',
    license='BSD',
    author=u'Michael Elsdörfer',
    author_email='michael@elsdoerfer.com',
    description=
        'ResellerClub API CLI client',
    py_modules=['resellerclub'],
    install_requires=['docopt>=0.6.1', 'requests>=2.0.0'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    entry_points="""[console_scripts]\rresellerclub = resellerclub:run\n""",
)
