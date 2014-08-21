# -*- coding: utf-8 -*-
#

"""
Package information for tinfo package.
"""

from setuptools import setup

VERSION = '1.0.0'

requires = [
    ]

setup(
        name='tinfo',
        description="Console extension to tmux",
        long_description=open('README.rst').read(),
        url="https://github.com/richo/tinfo",
        version=VERSION,
        author="Richo Healey",
        author_email="richo@psych0tik.net",
        license="MIT",
        packages=[
            'tinfo',
        ],
        entry_points={
            'console_scripts': [
                    'tinfo = tinfo:main',
                ],
        },
        install_requires=requires,
    )
