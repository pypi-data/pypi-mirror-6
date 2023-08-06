'''
Created on Apr 15, 2014

@author: sshuster
'''
import sys
import ConfigParser
from src.hdfs_load import HdfsLoad
import os


ARGS = ['config_file']
OPTIONS = ['']
USAGE = "usage: python hdfs_load.py {0}{1}"

def parse_config():
    if len(sys.argv)-1 != len(ARGS):
        print USAGE.format(' '.join(OPTIONS), ' '.join(ARGS))
        exit()
    else:
        config = ConfigParser.ConfigParser()
        config.readfp(open(sys.argv[1],'r'))
        return config

def main():
    config = parse_config()
    HdfsLoad(config)
    
if __name__ == "__main__":
    main()