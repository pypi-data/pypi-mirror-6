# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 20:23:47 2013

@author: kyle
"""

#!/usr/bin/env pythonS

from setuptools import setup, find_packages

with open('README.txt') as file:
    long_description = file.read()
    
setup(name='GLAMS',
      version='0.1.5',
      description='Gandhi Lab Animal Management System',
      license='MIT',
      long_description=long_description,
      author='Kyle Ellefsen',
      author_email='kyleellefsen@gmail.com',
      url='https://github.com/sunilgandhilab/GLAMS/',
      packages=find_packages(),
      install_requires=['cherrypy >= 3.2.2',
                        'mysql-connector-python >= 1.0.12',
                        'lxml >= 3.2.0' ],
      include_package_data=True,
     )