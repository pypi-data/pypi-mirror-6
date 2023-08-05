# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 20:23:47 2013

@author: kyle
"""

#!/usr/bin/env pythonS

from setuptools import setup

with open('README.txt') as file:
    long_description = file.read()
    
setup(name='GLAMS',
      version='0.1.0',
      description='Gandhi Lab Animal Management System',
      long_description=long_description,
      author='Kyle Ellefsen',
      author_email='kyleellefsen@gmail.com',
      url='https://github.com/sunilgandhilab/GLAMS/',
      packages=['glams','glams.glams','glams.glams.checkpassword','glams.glams.databaseInterface','glams.glams.website','glams.glams.website.admin','glams.glams.website.database','glams.glams.website.experimentlog','glams.glams.website.home','glams.glams.website.home.ajax','glams.glams.website.info'],      
      install_requires=['cherrypy >= 3.2.2',
                        'mysql-connector-python >= 1.0.12'],
      include_package_data=True,
     )