'''
Created on Apr 2, 2014

@author: sshuster
'''
import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "edmunds_hdfs_load",
    version = "1.21",
    author = "Sam Shuster",
    author_email = "sshuster@edmunds.com",
    description = ("Moves files to hdfs by creating hive tables "),
    license = "None",
    install_requires = ['paramiko>=1.0'],
    keywords = "hive hdfs",
    packages=['src', 'tests', 'documentation'],
    package_data={'sample_config':['allinfo_load.cfg']},
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    entry_points = {'console_scripts':['hdfs_load = src.hdfs_load:main']},
)