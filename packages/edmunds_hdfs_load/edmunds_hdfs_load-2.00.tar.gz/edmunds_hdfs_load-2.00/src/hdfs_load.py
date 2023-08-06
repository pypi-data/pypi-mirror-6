'''
Created on Apr 2, 2014

@author: sshuster
'''

import paramiko
import sys
import os
from paramiko import SFTPClient
import time
import csv
import create_hive_table_sql as cht
import ConfigParser

ARGS = ['config_file']
OPTIONS = ['']
USAGE = "usage: python hdfs_load.py {0}{1}"
TEMP_SUFFIX = '_temp'

#CONFIG_CONSTANTS
LOCAL_PATHS = "LocalPaths"
REMOTE_PATHS = "RemotePaths"
HDFS = "HDFSLocation"
CONNECTION = "RemotePaths"
HIVE = "Hive"
HIVE_DELIMITER = '\x1D'

SQL_FOLDER = "SQL_DDL"

PARTITION_COLUMNS = ['PartitionYear','PartitionMonth','PartitionDay']

def createSSHClient(server, user, password):
    '''Creates an SSH client'''
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=user, password=password)
    return client

def createClients(server, username, password):
    '''Creates an SSH and SFTP client'''
    ssh = createSSHClient(server, username, password)
    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    return ssh, sftp


def parse_config():
    if len(sys.argv)-1 != len(ARGS):
        print USAGE.format(' '.join(OPTIONS), ' '.join(ARGS))
        exit()
    else:
        config = ConfigParser.ConfigParser()
        config.readfp(open(sys.argv[1],'r'))
        return config

def move_folder(sftp, dest_folder, folder, delimiter=",", recursive=False, remove_headers=False, mv = "NA"):
    '''moves_folders recursively'''
    info_dict = {}
    try:
        sftp.mkdir(dest_folder)
    except:
        print "Destination folder already exists -> not making"
    for f in os.listdir(folder):
        if f[0] == '.':
            continue
        if f[0] == SQL_FOLDER:
            continue
        f_path = os.path.join(folder,f)
        dest_path = dest_folder + "/" + f
        if(os.path.isdir(f_path) and recursive):
            move_folder(sftp,dest_path,f_path,recursive,delimiter,recursive,remove_headers, mv)
        else:
            print "Copying {0} to {1}".format(f_path, dest_path)
            if remove_headers:
                try:
                    f_path, table_name, headers = preprocess_csv(f_path, delimiter, mv)
                    info_dict[table_name] = headers
                    sftp.put(f_path, dest_path)
                except:
                    "Copying {0} to {1} - FAILED! Skipping this file".format(f_path, dest_path)
                os.remove(f_path)
            else:
                sftp.put(f_path, dest_path)
    return info_dict

def check_remote_path(ssh, path):
    path_parts = path.split('/')
    cur_path = ""
    for segment in path_parts:
        cur_path += segment
        stdin, stdout, stderr = ssh.exec_command("mkdir {0}".format(cur_path))
        stdin.close()
        print stdout.read()
        print stderr.read()
        cur_path += "/"

def get_cur_date():
    year = time.strftime("%Y")
    month = time.strftime("%m")
    day = time.strftime("%d")
    tl = [year,month,day]
    return dict((k,v) for k,v in zip(PARTITION_COLUMNS,tl))

def process_tables(ssh, folder, partition_dict):
    stdin, stdout, stderr = ssh.exec_command('ls {0}'.format(folder))
    stdin.close()
    for line in stdout.read().splitlines():
        load_hive_data(ssh, folder+"/"+line, os.path.splitext(line)[0], partition_dict)
        
def load_hive_data(ssh, path, table_name, partition_dict): 
    hql_command = 'LOAD DATA LOCAL INPATH "{0}" OVERWRITE INTO TABLE {1} PARTITION ({2})'
    partition_string = reduce(lambda st,col_name: st+col_name+"=\""+partition_dict[col_name]+"\", ", partition_dict, '')[:-2]
    hql_command = hql_command.format(path, table_name, partition_string)
    run_hive_command = "hive -e '{0}'"
    print "Loading data into {0}".format(table_name)
    print hql_command
    stdin, stdout, stderr = ssh.exec_command(run_hive_command.format(hql_command))
    stdin.close()
    print stdout.read()
    print stderr.read()

def get_table_name(csv_file):
    return os.path.basename(os.path.splitext(csv_file)[0])
    
def preprocess_csv(csv_file, delimiter_in = ",", missing_values = "NA"):
    '''Gets headers and removes them from open file before transporting to destination'''
    n_file = csv_file + TEMP_SUFFIX
    with open(csv_file,'rb') as inp:
        with open(n_file,'wb') as out:
            csv_inp = csv.reader(inp,delimiter=delimiter_in)
            csv_out = csv.writer(out,delimiter=HIVE_DELIMITER)
            headers = csv_inp.next()
            table_name = get_table_name(csv_file)
            for line in csv_inp:
                csv_out.writerow(map(lambda x: "\N" if x == missing_values else x,line))
    return n_file, table_name, headers
            
def create_hive_ddl(ssh, sql_folder, table_name, fields, base_path, overwrite = False):
    config_dict = cht.parse_program_input(table_name, fields, ["STRING" for f in fields], base_path+"/"+table_name, PARTITION_COLUMNS)
    config_dict[cht.FDELIM] = HIVE_DELIMITER
    output_f_location = os.path.join(sql_folder,table_name+".sql")
    cht.create_creation_sql(config_dict, output_f_location)
    if overwrite:
        print "Dropping table {0}".format(table_name)
        try:
            stdin, stdout, stderr = ssh.exec_command('hive -e "DROP TABLE {0}"'.format(table_name))
            stdin.close()
            print stdout.read()
        except:
            print "No table exists to overwrite"
    
def create_hive_tables(sftp,ssh,sql_folder, dest_sql_folder):
    move_folder(sftp,dest_sql_folder,sql_folder)
    stdin, stdout, stderr = ssh.exec_command('ls {0}'.format(dest_sql_folder))
    stdin.close()
    for line in stdout.read().splitlines():
        cmd = 'hive -f '+dest_sql_folder+'/'+line
        print "Executing {0}".format(cmd)
        stdin2, stdout2, stderr2 = ssh.exec_command(cmd)
        stdin2.close()
        print stdout2.read()
        print stderr2.read()

def main():
    config = parse_config()
    src = config.get(LOCAL_PATHS,"local_dir")
    dest = config.get(REMOTE_PATHS,"dest_dir")
    hdfs_dest = config.get(HDFS,"hdfs_base_folder")
    sql_folder = os.path.join(src, SQL_FOLDER)
    sql_dest_folder = dest + "/" + SQL_FOLDER
    
    server = config.get(CONNECTION,"server")
    username = config.get(CONNECTION,"username")
    password = config.get(CONNECTION,"password")
    
    create_tables = config.get(HIVE,"create_tables") == "True"
    overwrite_existing = config.get(HIVE, "overwrite_existing_hive") == "True"
    delimiter = config.get(HIVE, "delimiter")
    missing_value = config.get(HIVE, "missing_value")
    
    ssh, sftp = createClients(server,username,password)
    check_remote_path(ssh,dest)
    check_remote_path(ssh,sql_dest_folder)
    info_dict = move_folder(sftp,dest,src,delimiter,True,True, missing_value)
    try:
        os.mkdir(sql_folder)
    except:
        "Print folder already exists "
    if create_tables:
        for tn in info_dict:
            create_hive_ddl(ssh, sql_folder,tn,info_dict[tn],hdfs_dest, overwrite_existing)
        create_hive_tables(sftp,ssh,sql_folder,sql_dest_folder)
    process_tables(ssh, dest, get_cur_date())
    
if __name__ == "__main__":
    main()