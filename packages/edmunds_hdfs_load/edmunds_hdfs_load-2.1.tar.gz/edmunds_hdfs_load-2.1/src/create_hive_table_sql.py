'''
Created on Mar 26, 2014

@author: sshuster
'''
import sys
import os

BASE_PATH = '!base_path'
TABLE_NAME = '!table_name'
COMMENT = '!comment'
CK = '!columns'
PARTITIONS = '!partitions'
SAMP_ABS_PATH = '!full_path'
FDELIM = '!delim'

RANGE_DELIM = "-"
LIST_DELIM = ","

FILE_DELIM = '29'

VAR = "$"
#SQL DATA TYPE CONVERSION
data_type_conversion = {"STRING":["VARCHAR","NVARCHAR","CHAR","DATE","TIME"],"DECIMAL":["NUMERIC"]}

#SQL CREATE COMMANDS
DROP_CMD = "DROP TABLE {0};\n"
CREATE_CMD = "CREATE EXTERNAL TABLE {0}(\n{1}\n)\n"
COMMENT_CMD = "COMMENT '{0}'\n"
PARTITION_CMD = "PARTITIONED BY ({0})\n"
FORMATBY_CMD = "ROW format delimited fields terminated by '{0}' STORED AS TEXTFILE\n"
LOCATION_CMD = "LOCATION '{0}';"

#SQL ALTER COMMANDS
ALTER_CMD = "ALTER TABLE {0} add if not exists PARTITION ({1}) location '{2}';\n"

#PYTHON_TYPE_CONVERSION
ptc = {int:"BIGINT",float:"DOUBLE",str:"STRING"}

class OrderedDict(object):
    
    def __init__(self):
        self.d = {}
        self.k = []
        
    def __setitem__(self,key,value):
        if not self.d.has_key(key):
            self.k.append(key)
        self.d[key] = value
    
    def __getitem__(self, key):
        return self.d[key]
    
    def keys(self):
        return self.k
    
    def has_key(self, key):
        return self.d.has_key(key)
    
    
def set_up_dictionary():
    config_dict = {}
    config_dict[CK] = OrderedDict()
    config_dict[PARTITIONS] = OrderedDict()
    config_dict[COMMENT] = None
    config_dict[TABLE_NAME] = None
    config_dict[SAMP_ABS_PATH] = None
    config_dict[BASE_PATH] = None
    config_dict[FDELIM] = FILE_DELIM 
    return config_dict

def sample_path_iterator(sample_path, partition_dict, depth=0):
    if depth >= len(partition_dict.keys()):
        yield sample_path, {}
    else:
        partition_name = partition_dict.keys()[depth]
        rep = VAR + partition_name
        for poss_val in partition_dict[partition_name]:
            it_down = sample_path_iterator(sample_path,partition_dict,depth+1)
            for path, cur_values in it_down:
                cur_path= path.replace(rep,poss_val)
                cur_values[partition_name] = poss_val
                yield cur_path, cur_values

def parse_program_input(table_name, fields, types, base_path, partitions):
    config_dict = set_up_dictionary()
    config_dict[TABLE_NAME] = table_name
    config_dict[BASE_PATH] = base_path
    for p in partitions:
        config_dict[PARTITIONS][p] = []
    for f,t in zip(fields,types):
        config_dict[CK][f] = t
    config_dict[SAMP_ABS_PATH] = base_path
    return config_dict

def get_hive_type(python_type):
    return ptc[python_type]

def parse_input(f_location):
    f = open(f_location,'r')
    config_dict = set_up_dictionary()
    for line in f:
        line = line.strip()
        if "#" not in line:
            if "=" in line:
                ckey, cvalue = line.split("=")
                ckey = ckey.strip()
                cvalue = cvalue.strip()
                if ckey == PARTITIONS:
                    cvalues = cvalue.split(',')
                    for part in cvalues:
                        part = part.strip()
                        config_dict[PARTITIONS][part] = []
                else:
                    if config_dict.has_key(ckey):
                        config_dict[ckey] = cvalue
                    else:
                        if config_dict[PARTITIONS].has_key(ckey):
                            config_dict[PARTITIONS][ckey] = handle_partition_ranges(cvalue)
                        else:
                            print "Incorrect setting name: {0}".format(ckey)
                            raise Exception
            else:
                names = line.split()
                if len(names)> 0:
                    config_dict[CK][names[0]] = names[1].upper()
    return config_dict

def handle_partition_ranges(full_range):
    ret_range = []
    list_values = full_range.split(LIST_DELIM)
    for list_value in list_values:
        list_value = list_value.strip()
        if RANGE_DELIM in list_value:
            start, finish = list_value.split(RANGE_DELIM)
            try:
                min_length = max(len(start),len(finish))
                start = int(start)
                finish = int(finish)
                for i in range(start,finish+1):
                    val = str(i)
                    val = val.zfill(min_length)
                    ret_range.append(val)
            except:
                print "Range values must be integers!"
                raise Exception
        else:
            ret_range.append(list_value)
    return ret_range

def build_column_string(column_dict):
    rdc = dict((k,v) for v in data_type_conversion.keys() for k in data_type_conversion[v])
    ret = ""
    for c_name in column_dict.keys():
        c_type = column_dict[c_name]
        if rdc.has_key(c_type):
            print 'WARNING: one of your types {0} is not valid in Hive, converting to {1}'.format(c_type,rdc[c_type])
            c_type = rdc[c_type]
        ret += c_name + " " + c_type + ",\n"
    return ret[:-2]
        
def build_partition_string(partition_dict):
    ret = ""
    for partition_name in partition_dict.keys():
        ret += partition_name + " string, "
    return ret[:-2]

def create_creation_sql(config_dict, output_f_location):
    create_sql_f = open(output_f_location,'w')
    columns_string = build_column_string(config_dict[CK])
    create_sql_f.write(CREATE_CMD.format(config_dict[TABLE_NAME],columns_string))
    create_sql_f.write(COMMENT_CMD.format(config_dict[COMMENT]))
    partition_string = build_partition_string(config_dict[PARTITIONS])
    create_sql_f.write(PARTITION_CMD.format(partition_string))
    create_sql_f.write(FORMATBY_CMD.format(config_dict[FDELIM]))
    create_sql_f.write(LOCATION_CMD.format(config_dict[BASE_PATH]))

def build_alter_partition_string(cur_values, partition_dict):
    ret_string = ""
    for partition in partition_dict.keys():
        ret_string += partition + "=" + cur_values[partition] + ","
    return ret_string[:-1]
    
def create_alter_sql(config_dict, output_f_location):
    create_alter_f = open(output_f_location, 'w')
    sample_path = config_dict[SAMP_ABS_PATH]
    sample_path = sample_path.replace(VAR+BASE_PATH[1:],config_dict[BASE_PATH])
    it = sample_path_iterator(sample_path,config_dict[PARTITIONS])
    for cur_path, cur_values in it:
        partition_string = build_alter_partition_string(cur_values,config_dict[PARTITIONS])
        create_alter_f.write(ALTER_CMD.format(config_dict[TABLE_NAME],partition_string,cur_path))

def main():        
    input_file = sys.argv[1]
    output_folder = sys.argv[2]    
    config_dict = parse_input(input_file)
    base_name = config_dict[TABLE_NAME]
    outbase = os.path.join(output_folder,base_name) 
    create_creation_sql(config_dict,outbase+".sql")
    create_alter_sql(config_dict,outbase+"_alter.sql")
    
if __name__ == "__main__":
    main()
            