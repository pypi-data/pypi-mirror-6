# encoding: utf-8
import cherrypy
from glams.databaseInterface import databaseInterface as DI
from glams.databaseInterface.connect import importconfig

def checkPassword():
    '''Simply checks if a cookie is set.  If it is, return users name'''
    cookie = cherrypy.request.cookie
    if len(cookie)>0:
        try:
            name = cookie['sida'].value
            hashedpassword = cookie['sidb'].value
            if DI.isUser(name, hashedpassword):
                return name
        except KeyError:
            pass
    return None

config=importconfig()
salt=config['salt']
            

    
