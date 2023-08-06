#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup
import sys

install_requires = [
    'flask'
]

if sys.version_info < (2, 7, 0):
    install_requires.append('argparse')

setup(
    name='remosh',
    version='0.1.3',
    author='Tarjei Husøy',
    author_email='tarjei@roms.no',
    url='https://github.com/thusoy/remosh',
    description="A remote execution engine",
    py_modules=['remosh'],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'remosh = remosh:main',
        ]
    },
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        # 'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
