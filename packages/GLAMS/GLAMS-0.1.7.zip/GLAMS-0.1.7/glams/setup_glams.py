# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 14:55:58 2013

@author: kyle
"""
import os.path
import time

def main():
    if os.path.isfile('config.txt'):
        print("""\n\n****WARNING****\n\n DO NOT RUN THIS FILE IF YOU HAVE ALREADY ADDED INFORMATION TO THE DATABASE!!!\n\nTHIS FILE WILL RESET YOUR DATABASE.\n\nYou're trying to run setup.py but you already have a config file. You can edit the information in your config file in a text editor.  If you still want to run this file and reset your database, delete your 'config.txt' file.""")
    else:
        mysql_IP_address=raw_input('Enter the ip address of your mysql server (leave blank if running on this computer): ')
        if mysql_IP_address=='':
            mysql_IP_address='localhost'
        database=raw_input('Enter the name of the MySQL database (e.g. glams): ')
        if database=='':
            database='glams'
        user=raw_input('Enter the name of the user you created to access the mysql database: ')
        password=raw_input("Enter the password for user '{}':".format(user))
        port=raw_input("Enter the port to access your mysql server (leave blank for the default '3306'): ")
        if port=='':
            port='3306'
        salt=raw_input("Enter a 5-10 character random combination of characters to use as a salt for better password encryption: ")
        
        config="""mysql_IP_address={0}
user={1}
database={2}
password={3}
port={4}
salt={5}
calendarTag=<p>No Calendar Yet</p>""".format(mysql_IP_address,user,database,password,port,salt)
        
        f=open('config.txt', 'w')
        f.write(config)
        f.close()
        print('Creating GLAMS database')
        time.sleep(2)
        from glams.databaseInterface.reset import reset
        reset()
        print('Sucessfully created GLAMS database')
        

        
    

if __name__=='__main__':
    main()
