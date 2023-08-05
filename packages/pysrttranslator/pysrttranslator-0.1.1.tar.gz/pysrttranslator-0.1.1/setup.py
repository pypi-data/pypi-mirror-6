#-*- encoding: utf-8 -*-
from distutils.core import setup

setup(
    name='pysrttranslator',
    version='0.1.1',
    author='Nhomar Hernández',
    author_email='nhomar@vauxoo.com',
    packages=['pysrttranslator'],
    scripts=['bin/pysrttranslator'],
    url='http://pypi.python.org/pypi/pysrttranslator',
    install_requires=[
        "google-api-python-client>=1.2",
        "pysrt>=0.5.1",
    ],
    license='LICENSE.txt',
    description='Transate srt subtitles with python and google translator api.',
    long_description=open('README').read(),
)
