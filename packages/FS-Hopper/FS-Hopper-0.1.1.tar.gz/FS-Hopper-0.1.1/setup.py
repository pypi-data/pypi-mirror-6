from setuptools import setup

setup(
name='FS-Hopper',
version='0.1.1',
author='Brian Wiborg',
author_email='baccenfutter@c-base.org',
packages=['fs_hopper'],
scripts=[],
url='http://pypi.python.org/pypi/FS-Hopper/',
license='LICENSE.txt',
description='Simple object-oriented access to a filesystem directory tree',
long_description=open('README.txt').read(),
install_requires=['python-ldap >= 2.4.13'],
)

