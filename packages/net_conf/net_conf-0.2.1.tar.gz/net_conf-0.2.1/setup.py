from setuptools import setup

setup(
name='net_conf',
version='0.2.1',
author='Brian Wiborg',
author_email='baccenfutter@c-base.org',
packages=['net_conf'],
scripts=[],
url='http://pypi.python.org/pypi/net_conf/',
license='LICENSE.txt',
description='Commandline-based network manager',
long_description=open('README.txt').read(),
install_requires=['ipaddr==2.1.7'],
)

