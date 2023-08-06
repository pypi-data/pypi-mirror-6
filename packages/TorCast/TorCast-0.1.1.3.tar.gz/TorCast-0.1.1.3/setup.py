#coding=utf8
from setuptools import setup

__author__ = 'alex'

setup(
    name='TorCast',
    version='0.1.1.3',
    packages=['TorCast'],
    author='Alexander.Li',
    author_email='superpowerlee@gmail.com',
    license='LGPL',
    install_requires=["tornado>=2.4.1",],
    description="Broadcast messages to all tornado process subcribed on Redis asynchronously Or Block on Redis Queue asynchronously",
    keywords ='tornado asynchronous redis message',
    url="https://github.com/ipconfiger/TorCast"
)