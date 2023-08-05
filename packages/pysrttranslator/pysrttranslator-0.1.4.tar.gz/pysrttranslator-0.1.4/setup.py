#-*- encoding: utf-8 -*-
from distutils.core import setup

setup(
    name='pysrttranslator',
    version='0.1.4',
    author='Nhomar Hernández',
    author_email='nhomar@vauxoo.com',
    mantainer='Nhomar Hernández',
    mantainer_email='nhomar@vauxoo.com',
    packages=['pysrttranslator'],
    scripts=['bin/pysrttranslator'],
    url='http://pypi.python.org/pypi/pysrttranslator',
    install_requires=[
        'google-api-python-client>=1.2',
        'pysrt>=0.5.1',
        'configglue>=1.1.2',
    ],
    license='LICENSE.txt',
    platform=['Linux'],
    description='Transate srt subtitles with python and google translator api.',
    long_description=open('docs/source/general.rst').read(),
)
