#!/usr/bin/env python

# import os
# import sys
# import glob

from setuptools import setup

data_files = [
    ('share/doc/sxxexx', ['AUTHORS', 'README.md'])
]

setup(
    name='sxxexx',
    version='0.2',
    description="A command line tool to search (and download) series from the Piracy Bay",
    long_description=open('README.md').read(),
    author='Nicolas Hennion',
    author_email='nicolas@nicolargo.com',
    url='https://github.com/nicolargo/sxxexx',
    license="MIT",
    keywords="torrent search download serie",
    packages=['sxxexx'],
    include_package_data=True,
    data_files=data_files,
    # test_suite="witsub.test",
    entry_points={"console_scripts": ["sxxexx=sxxexx.sxxexx:main"]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Environment :: Console',
    ]
)
