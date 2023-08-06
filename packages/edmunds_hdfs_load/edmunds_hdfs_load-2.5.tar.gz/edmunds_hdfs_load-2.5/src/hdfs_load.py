'''
Created on Apr 2, 2014

@author: sshuster
'''
import os
import shutil

import time
import csv
import create_hive_table_sql as cht

from src.hdfs_load_cygwin import CygwinSSH
try:
    from src.paramiko_connector import ParamikoWrapper
except ImportError:
    ParamikoWrapper = None
    print "No Paramiko installed!"
    exit()



class HdfsLoad(object):
    
    #CONFIG_CONSTANTS
    LOCAL_PATHS = "LocalPaths"
    REMOTE_PATHS = "RemotePaths"
    HDFS = "HDFSLocation"
    CONNECTION = "RemotePaths"
    HIVE = "Hive"
    CYGWIN = "Cygwin"
    
    SQL_FOLDER = "SQL_DDL"
    
    HIVE_DELIMITER = '\x1D'
    TEMP_SUFFIX = '_temp'
    SQL_FOLDER = "SQL_DDL"
    
    PART_PREFIX = "part_"
    
    PARTITION_COLUMNS = ['PartitionYear','PartitionMonth','PartitionDay']
    
    def __init__(self, config):
        #self.using_cygwin = config.get(self.CYGWIN,"using_cygwin") == "True"
        self.using_cygwin = False
    
        self.src = config.get(self.LOCAL_PATHS,"local_dir")
        self.dest = config.get(self.REMOTE_PATHS, "base_remote") + "/" + os.path.basename(self.src) + "/"
        self.hdfs_dest = config.get(self.HDFS,"hdfs_base_folder")
        self.sql_folder = os.path.join(self.src, self.SQL_FOLDER)
        self.sql_dest_folder = self.dest + "/" + self.SQL_FOLDER + "/"
        
        self.server = config.get(self.CONNECTION,"server")
        self.username = config.get(self.CONNECTION,"username")
        self.password = config.get(self.CONNECTION,"password")
        
        self.create_tables = config.get(self.HIVE,"create_tables") == "True"
        self.overwrite_existing = config.get(self.HIVE, "overwrite_existing_hive") == "True"
        self.delimiter = config.get(self.HIVE, "delimiter")
        self.missing_values = config.get(self.HIVE, "missing_value")
        self.table_prefix = config.get(self.HIVE, "table_prefix")
        
        if self.using_cygwin:
            self.ssh_client = CygwinSSH(self.server,self.username,self.password)
        else:
            self.ssh_client = ParamikoWrapper(self.server,self.username,self.password)
        
        #Ensure that paths exist
        self.check_paths()
        
        #The flist containing all of the PATHS of the file names  
        self.f_list = [f for f in os.listdir(self.src) if f[0] != "." and f != self.SQL_FOLDER and not os.path.isdir(f)]
        
        #Info dict holds all of the type and field information keyed by file name
        self.info_dict = {}
        #Cycle through each file in the path
        
        self.dest_f_list = []
        for f_in in self.f_list:
            f_in_path = os.path.join(self.src, f_in)
            f_out_path = os.path.join(self.src,self.get_temp_file(f_in))
            try:
                self.info_dict[f_in] = self.preprocess_table(f_in_path, f_out_path)
                gzipped_fname = self.move_table(f_in_path, f_out_path)
                self.dest_f_list.append(gzipped_fname)
            except Exception as e:
                print e
                print "Error!"
            os.remove(f_out_path)
        if self.create_tables:
            try:
                os.mkdir(self.sql_folder)
            except:
                shutil.rmtree(self.sql_folder)
                os.mkdir(self.sql_folder)
            for f in self.info_dict:
                self.create_hive_ddl(f)
            self.move_ddl()
            self.create_tables_function()
        
        self.load_data()
            
    def check_paths(self):
        self.check_remote_path(self.dest)
        self.check_remote_path(self.sql_dest_folder)
    
    def check_remote_path(self,path):
        path_parts = path.split('/')
        command = "rm {0}/*".format(path)
        stdout, stderr = self.ssh_client.exec_command(command)
        print stdout, stderr
        cur_path = ""
        for segment in path_parts:
            if segment != "":
                cur_path += segment
                command = "/bin/mkdir {0}".format(cur_path)
                stdout, stderr = self.ssh_client.exec_command(command)
                print stdout
                print stderr
            cur_path += "/"
 
    def get_table_name(self, f_name):
        '''Retursn the table name based off of a file name'''
        return self.table_prefix + os.path.basename(f_name).split('.')[0]
            
    def preprocess_table(self, f_in, f_out):
        '''Preprocesses a csv file also calls preproces line'''
        print "Preprocessing {0} to {1}".format(f_in, f_out)
        with open(f_in,'rb') as inp:
            with open(f_out,'wb') as out:
                csv_inp = csv.reader(inp,delimiter=self.delimiter)
                csv_out = csv.writer(out,delimiter=self.HIVE_DELIMITER)
                headers = csv_inp.next()
                type_list = [None for _ in headers]
                for line in csv_inp:   
                    new_line = self.process_line(line,type_list)
                    csv_out.writerow(new_line)
        return (headers, type_list)
    
    def get_temp_file(self, in_file):
        '''Gets the name of a preprocessed temp file'''
        return in_file + self.TEMP_SUFFIX
    
    def process_line(self, line, type_list):
        '''Preprocesses the csvs'''
        new_line = []
        for ind,el in enumerate(line):
            if el == self.missing_values:
                new_line.append("\N")
            else:
                if type_list[ind] is None:
                    try:
                        type_list[ind] = cht.get_hive_type(type(eval(el)))
                    except:
                        type_list[ind] = "STRING"
                new_line.append(el)
        return new_line
    
    def get_sql_f_name(self, f_name):
        '''Returns the sql file name'''
        return os.path.basename(f_name)+".sql"
    
    def move_table(self, in_file, out_file):
        '''Moves a table to the production hadoop clsuter and then gzips it'''
        print "Moving to: " + self.dest + os.path.basename(in_file)
        self.ssh_client.put(out_file,self.dest + self.get_dest_file_name(os.path.basename(in_file)))
        self.ssh_client.exec_command('gzip {0}'.format(self.dest + self.get_dest_file_name(os.path.basename(in_file))))
        return os.path.basename(in_file) + ".gz"
            
    def create_hive_ddl(self, f_name):
        '''Creates the hive ddl by calling the create_hive_table_sql class'''
        table_name = self.get_table_name(f_name)
        config_dict = cht.parse_program_input(table_name, self.info_dict[f_name][0], self.info_dict[f_name][1], self.hdfs_dest+"/"+table_name, self.PARTITION_COLUMNS)
        config_dict[cht.FDELIM] = self.HIVE_DELIMITER
        output_f_location = os.path.join(self.sql_folder, self.get_sql_f_name(f_name))
        cht.create_creation_sql(config_dict, output_f_location)
        if self.overwrite_existing:
            print "Dropping table {0}".format(table_name)
            try:
                stdout, stderr = self.ssh_client.exec_command('hive -e "DROP TABLE {0}"'.format(table_name))
                print stdout
            except:
                print "No table exists to overwrite"
                
    def move_ddl(self):
        '''Moves the ddl to the production hadoop cluster'''
        for in_file in self.f_list:
            sql = self.get_sql_f_name(in_file)
            self.ssh_client.put(os.path.join(self.sql_folder,sql),self.sql_dest_folder + sql)
            
    def create_tables_function(self):
        '''Calls the create table command on production hadoop cluster'''
        for in_file in self.f_list:
            sql = self.get_sql_f_name(in_file)
            cmd = 'hive -f '+self.sql_dest_folder+sql
            print "Executing {0}".format(cmd)
            stdout2, stderr2 = self.ssh_client.exec_command(cmd)
            print stdout2
            print stderr2
           
    def get_cur_date(self):
        '''Gets the current date to be used for the partitions'''
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%d")
        tl = [year,month,day]
        return dict((k,v) for k,v in zip(self.PARTITION_COLUMNS,tl))
    
    def get_dest_file_name(self, f_path):
        return self.PART_PREFIX+f_path
     
    def load_data(self):
        '''Calls the load data command in production hadoop cluster'''
        partition_dict = self.get_cur_date()
        for in_file in self.dest_f_list:
            cur_unix_path = self.dest+"/"+self.get_dest_file_name(in_file)
            table_name = self.get_table_name(in_file)
            hql_command = 'LOAD DATA LOCAL INPATH "{0}" OVERWRITE INTO TABLE {1} PARTITION ({2})'
            partition_string = reduce(lambda st,col_name: st+col_name+"=\""+partition_dict[col_name]+"\", ", partition_dict, '')[:-2]
            hql_command = hql_command.format(cur_unix_path, table_name, partition_string)
            run_hive_command = "hive -e '{0}'"
            print "Loading data into {0}".format(table_name)
            print hql_command
            stdout, stderr = self.ssh_client.exec_command(run_hive_command.format(hql_command))
            print stdout
            print stderr

