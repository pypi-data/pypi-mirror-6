'''
Created on Apr 2, 2014

@author: sshuster
'''
import os
from setuptools import setup, find_packages
#import py2exe

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "edmunds_hdfs_load",
    version = "2.5",
    author = "Sam Shuster",
    author_email = "sshuster@edmunds.com",
    description = ("Moves files to hdfs by creating hive tables "),
    license = "None",
    install_requires = ['paramiko>=1.0'],
    keywords = "hive, hdfs",
    packages=['','src', 'documentation'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    package_data = {
        # If any package contains *.txt files, include them:
        '': ['*.txt','*.cfg', '*.docx', '*.doc'],
        # And include any *.dat files found in the 'data' subdirectory
        # of the 'mypkg' package, also:
    },
    #data_files = {'',['run_main']}
    #console = ['main.py']
)