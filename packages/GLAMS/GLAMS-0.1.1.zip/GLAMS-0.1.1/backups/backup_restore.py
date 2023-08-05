# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 18:06:27 2013

@author: kyle
"""

import os, datetime, codecs

#### EDIT THESE PATHS IF THEIR LOCATION DIFFERS ON YOUR SYSTEM ####
pathToMysqldump="C:\\Program Files\\MySQL\\MySQL Server 5.6\\bin\\mysqldump"
pathToMysql="C:\\Program Files\\MySQL\\MySQL Server 5.6\\bin\\mysql"
#####################################################################


### GET database connection info from config.txt
filename=os.getcwd().split(os.sep)[:-1]

filename.append('glams'+os.sep+'config.txt')
filename=os.sep.join(filename)
BOM = codecs.BOM_UTF8.decode('utf8')
config=dict()
with codecs.open(filename, encoding='utf-8') as f:
    for line in f:
        line = line.lstrip(BOM)
        line=line.split('=')
        config[line[0].lstrip().rstrip()]=line[1].lstrip().rstrip()
user=str(config['user'])
database=str(config['database'])
password=str(config['password'])

def backupDB():
    outputFile='glams_backup_'+datetime.datetime.today().strftime("%Y.%m.%d.%H.%m.%S")+'.sql'
    command='\"\"{0}\" -u {1} -p{2} {3} >{4}\"'.format(pathToMysqldump, user, password, database, outputFile)
    value=os.system(command)
    print(value)

def restore(filename):
    command='\"\"{0}\" -u {1} -p{2} {3} < {4}\"'.format(pathToMysql, user, password, database, filename)
    value=os.system(command)
    print(value)
    
if __name__=='__main__':
    backupDB()