#!/usr/bin/env python
# vi:si:et:sw=4:sts=4:ts=4
# encoding: utf-8
try:
    from setuptools import setup
except:
    from distutils.core import setup

def get_version():
    return 6 #import subprocess
    version = subprocess.check_output(['git', 'rev-list', 'HEAD', '--count'])
    return version.strip()

setup(
    name="hostb_client",
    version=get_version() ,
    description='''hostb_client is a command line client for hostb.''',
    author="j",
    author_email="j@mailb.org",
    url="http://r-w-x.org/?p=hostb_client.git;a=summary",
    download_url="https://hostb.org/client/",
    license="GPLv3",
    scripts = [
        'bin/hostb_client',
    ],
    packages=[
        'hostb_client'
    ],
    install_requires=[
    ],
    keywords = [
],
    classifiers = [
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
)

