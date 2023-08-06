#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'suds',
]

setup(
    name='sermon-audio',
    version='0.0.8',
    author='Nathaniel Pardington',
    url='https://github.com/npardington/sermon-audio-api',
    download_url = 'https://github.com/npardington/sermon-audio-api/tarball/0.0.8',
    description='A python wrapper to the Sermon Audio API.',
    long_description=open('readme.md').read(),
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,

    license='MIT',
    include_package_data=True,

    classifiers=[
        'Programming Language :: Python'
    ],
)