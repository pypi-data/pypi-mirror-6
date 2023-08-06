# encoding: utf-8
import mysql.connector
import codecs
import threading


def importconfig():
    '''this function loads the config.txt file into a dictionary which is used by the 'connect.py' module.
    config.txt is a file which includes database connection information'''
    config=dict()
    filename='config.txt'
    BOM = codecs.BOM_UTF8.decode('utf8')
    with codecs.open(filename, encoding='utf-8') as f:
        for line in f:
            line = line.lstrip(BOM)
            line=line.split('=',1)
            config[line[0].lstrip().rstrip()]=line[1].lstrip().rstrip()
    return config

lock=threading.Lock()
class DB:
    cnx=None
    def __init__(self):
        self.config=importconfig()
    def connect(self):
        self.cnx=mysql.connector.connect(host=str(self.config['mysql_IP_address']), 
                                         user=str(self.config['user']), 
                                         database=str(self.config['database']), 
                                         password=str(self.config['password']), 
                                         port=int(self.config['port']))

        self.cursor=self.cnx.cursor(buffered=True)
    def execute(self,command, entriesTuple=None, commit=True):
        with lock:
            self.connect()
            self.cursor.execute(command,entriesTuple)
            #except mysql.connector.errors.ProgrammingError as e:
             #   self.cnx.close()
             #   print(e.msg)
             #   return e
            try:
                data=self.cursor.fetchall()
            except mysql.connector.errors.InterfaceError:
                data=tuple()
            self.cursor.close()
            if commit:
                self.cnx.commit()
            return data
            self.cnx.close()
db=DB()

class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None
        
class DB2:
    cnx=None
    def __init__(self):
        self.config=importconfig()
    def connect(self):
        self.cnx=mysql.connector.connect(host=str(self.config['mysql_IP_address']), 
                                         user=str(self.config['user']), 
                                         database=str(self.config['database']), 
                                         password=str(self.config['password']), 
                                         port=int(self.config['port']))
        self.cursor=self.cnx.cursor(buffered=True, cursor_class=MySQLCursorDict)
    def execute(self,command, entriesTuple=None, commit=True):
        with lock:
            self.connect()
            self.cursor.execute(command,entriesTuple)
            #except mysql.connector.errors.ProgrammingError as e:
             #   self.cnx.close()
             #   print(e.msg)
             #   return e
            try:
                data=self.cursor.fetchall()
            except mysql.connector.errors.InterfaceError:
                data=tuple()
            self.cursor.close()
            if commit:
                self.cnx.commit()
            return data
            self.cnx.close()
db2=DB2()