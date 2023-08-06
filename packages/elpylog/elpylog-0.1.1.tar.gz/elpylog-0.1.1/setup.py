#!/usr/bin/env python

from setuptools import setup

setup(
    name='elpylog',
    version='0.1.1',
    keywords='logging elasticsearch bulk udp logstash',
    description="Python logger sending it's logs to elasticsearch.",
    #long_description=open('README.md').read(),

    author='Koert van der Veer',
    author_email='opensource@ondergetekende.nl',
    download_url='https://github.com/ondergetekende/elpylog/tarball/v0.1.0',
    include_package_data=True,
    license='BSD License',
    packages=['elpylog'],
    url='git@github.com:ondergetekende/elpylog.git',
    zip_safe=False,
)
