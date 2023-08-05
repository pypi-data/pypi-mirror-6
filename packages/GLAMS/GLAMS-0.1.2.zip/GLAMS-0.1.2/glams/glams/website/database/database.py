# -*- coding: utf-8 -*-
import cherrypy
from glams.checkpassword.checkpassword import checkPassword
from glams.databaseInterface.connect import db, db2
from glams.glamsTemplate import glamsTemplate
from glams.website.database.classes import Mouse, Cage, date2str, getAge
from glams.website.database.forms import getMouseForm, getCageForm, getInnerCageForm, getGeneticFilterForm, getResident, getStrainList, getLabMemberList
import urllib2, datetime
from lxml import etree
from lxml.builder import E
from copy import deepcopy
#import os

def getBreedingStatusList():
    return ['','breeding','retired breeder','virgin','unknown']
def getLifeStatusList():
    return ['', 'alive','euthanized','missing','transferred']
def getSexList():
    return ['unknown', 'male', 'female']
def getZygosityList():
    return ['','++','+-','--','+?','-?','??','+/y','+/x']
def getAllMouseColumns():
    return ['mousename','strain','sex','life_status','breeding_status','DOB','DOD','cause_of_death','tag','mouse_notes','genotyped','cagename','mother','father','reserve_lab_member','reserve_date','reserve_description','reserve_filenames','reserve_notes','reserve_status','genetics'] #all these fields come from classes.Mouse.getFromDB
def getAllCageColumns():
    return ['cagename2','cagenotes','date_activated','date_inactivated','location','active','caretaker','residents','expectingpl','cagegroup'] #all these fields come from classes.Cage.getFromDB
def getPrettyText(column):
    """ This function takes the names of the column fields, as used in Ajax.refresh, and returns the pretty version which will be displayed in the browser"""
    convert={'':'', 'mousename':'Mouse',   'strain':'Strain','sex':'Sex',
             'life_status':'Life Status','breeding_status':'Breeding Status',
             'DOB':'DOB','DOD':'DOD','cause_of_death':'Cause of Death',
             'tag':'Tag','mouse_notes':'Notes','genotyped':'Genotyped',
             'cagename':'Cage','cagename2':'Cage','mother':'Mother',
             'father':'Father','reserve_lab_member':'Experimenter','reserve_filenames':'File Names',
             'reserve_date':'Experiment Date','reserve_description':'Experiment Description','reserve_notes':'Experiment Notes','reserve_status':'Experiment Status',
             'cagename':'Cage','cagenotes':'Cage Notes','date_activated':'Date Activated',
             'date_inactivated':'Date Inactivated','location':'Location',
             'active':'Active','caretaker':'Caretaker','genetics':'Genetics','residents':'Residents','expectingpl':'Breeding','cagegroup':'Cage Group'}
    return convert[column]
    
html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }
def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)
    
    
def getcagehistory(cagename):
    answer=db2.execute("""SELECT m.name AS mousename, m.id AS mouseID, h.start_date, h.end_date, h.start_date=(SELECT DOB FROM mice WHERE mice.id=m.id) AS bornhere,
                h.end_date=(SELECT DOD FROM mice WHERE mice.id=m.id) AS diedhere,
                (SELECT MIN(c.name) FROM cages AS c LEFT JOIN housing AS h2 ON h2.cage_id=c.id WHERE h2.end_date=h.start_date AND h2.mouse_id=m.id) AS cagebefore,
                (SELECT MIN(c.name) FROM cages AS c LEFT JOIN housing AS h2 ON h2.cage_id=c.id WHERE h2.start_date=h.end_date AND h2.mouse_id=m.id) AS cageafter
                FROM cages AS c 
                LEFT JOIN housing AS h ON c.id=h.cage_id 
                LEFT JOIN mice AS m ON m.id=h.mouse_id 
                WHERE c.name=%s""",(cagename,))
    # we are getting mice who were introduced, mice who were moved out, mice who were born in this cage, mice who were killed in this cage
    timeline=list()
    for m in answer:
        if m['mousename'] is not None:
            name=E.span({'onclick':"clickedOnMouseName('{}');".format(m['mouseID'])},m['mousename'])
            
            ### movement into a cage
            if m['bornhere']==1:
                timeline.append([m['start_date'], E.td(deepcopy(name)," born")])
            elif m['cagebefore'] is not None:
                timeline.append([m['start_date'], E.td(deepcopy(name),' introduced from '+m['cagebefore'])])
            else:
                timeline.append([m['start_date'],E.td(deepcopy(name), ' introduced')])                
            ### movement out of a cage
            if m['end_date'] is not None:
                if m['diedhere']==1:
                    timeline.append([m['end_date'],E.td(deepcopy(name)," died")])
                elif m['cageafter'] is not None:
                    timeline.append([m['end_date'],E.td(deepcopy(name)," moved to "+m['cageafter'])])
                else:
                    timeline.append([m['end_date'],E.td(deepcopy(name)," moved out")])
    timeline.sort()
    return timeline

    
def makequery(viewtype,c):
    ''' 
    This function creates a mysql query using a dict of all the columns paired with their filters
    sample query: "SELECT c.id, c.name AS cagename2, c.notes AS cagenotes, c.date_activated, c.date_inactivated, c.location, c.active, lab_members.name AS caretaker FROM cages as c LEFT JOIN care_taker AS ct ON ct.cage_id=c.id LEFT JOIN lab_members ON ct.lab_member_id=lab_members.id ORDER BY cagename2"
    viewtype - either 'mouseview' or 'cageview'
    c - the a dictionary of filters.  the keys are the names of the columns.  eg {'cagename':None,'active':[['active',1]]}
    
    '''    
    if viewtype is None:
        viewtype='mouse'
    MouseAlias={'mousename':'m.name as mousename','strain':'m.strain','sex':'m.sex','life_status': 'm.life_status',
                'breeding_status':'m.breeding_status','DOB':'m.DOB','DOD':'m.DOD','cause_of_death':'m.cause_of_death','tag':'m.tag','mouse_notes':'m.notes AS mouse_notes', 
                'genotyped':'m.genotyped','cagename':'cages.name AS cagename', 'mother':'mom.name AS mother','father':'dad.name AS father',
                'reserve_lab_member':'lab_members.name AS reserve_lab_member', 'reserve_date':'experiments.date AS reserve_date', 'reserve_filenames':'experiments.filenames AS reserve_filenames',
                'reserve_description':'experiments.description AS reserve_description','reserve_notes':'experiments.notes AS reserve_notes', 
                'reserve_status':'experiments.status AS reserve_status','genetics':'genes.name AS genename, genetics.zygosity'}
    CageAlias={'cagename2':'c.name AS cagename2','cagenotes':'c.notes AS cagenotes','date_activated':'c.date_activated','date_inactivated':'c.date_inactivated',
               'location':'c.location', 'active':'c.active','caretaker':'lab_members.name AS caretaker','cagegroup':'c.cagegroup',
               'residents':"m.name AS resident, m.id AS mouseID, litters.DOB AS litterDOB, m.sex, m.DOB, IF(EXISTS(SELECT * from experiments WHERE mouse_id=m.id), 'reserved','notreserved') AS reserved, h.currentcage ",
               'expectingpl':'c.expectingpl'}
    WhereAlias={     'mousename':'m.name COLLATE UTF8_GENERAL_CI LIKE  %(mousename)s', # the 'COLLATE UTF8_GENERAL_CI' makes it case insensitive, I'm not sure how.
                     'strain':'m.strain=%(strain)s',
                     'sex':'m.sex=%(sex)s',
                     'location':'c.location=%(location)s',   
                     'life_status':'m.life_status=%(life_status)s',
                     'breeding_status':'m.breeding_status=%(breeding_status)s',
                     'genotyped':'m.genotyped=%(genotyped)s',
                     'cagename':'cages.name COLLATE UTF8_GENERAL_CI LIKE %(cagename)s',
                     'mother':'mom.name=%(mother)s',
                     'father':'dad.name=%(father)s',
                     'reserve_lab_member':'lab_members.name=%(reserve_lab_member)s',
                     'reserve_description':'experiments.description=%(description)s',
                     'active':'c.active=%(active)s',
                     'expectingpl':'c.expectingpl=%(expectingpl)s',
                     'cagename2':'c.name LIKE %(cagename2)s',
                     'caretaker':'lab_members.name=%(caretaker)s',
                     'cagenotes':'c.notes LIKE %(cagenotes)s',
                     'cagegroup':'c.cagegroup LIKE %(cagegroup)s',
                     'mouse_notes':'m.notes LIKE %(mouse_notes)s',
                     'DOB':'m.DOB>=%(DOB0)s AND m.DOB <= %(DOB1)s',
                     'DOD':'m.DOD>=%(DOD0)s AND m.DOD <= %(DOD1)s',
                     'reserve_date':'experiments.date >= %(reserve_date0)s AND experiments.date <= %(reserve_date1)s',
                     'date_activated':'c.date_activated >= %(date_activated0)s AND c.date_activated <= %(date_activated1)s',
                     'date_inactivated':'c.indate_activated >= %(date_inactivated0)s AND c.date_inactivated <= %(date_inactivated1)s'
                 }
    d=dict() #d is a dictionary of arguments that will be the second argument in the mysql query, in order to prevent a mysql injection
    for k in WhereAlias.keys():
        if k in c.keys() and c[k] is not None:
            if k in set(['mousename','cagename2','cagename','cagenotes','mouse_notes', 'cagegroup']):
                c[k][0][1]='%'+c[k][0][1]+'%' #this makes the filter in mysql have wildcards before and after
            if (viewtype=='mouse' and k in MouseAlias.keys()) or (viewtype=='cage' and k in CageAlias.keys()):
                if k=='genetics':
                    pass
                else:
                    if len(c[k])==1:
                        d[k]=c[k][0][1]
                    elif len(c[k])==2: # for a date range
                        d[k+'0']=c[k][0][1]
                        d[k+'1']=c[k][1][1]
                    c[k]=WhereAlias[k]
    q=[] #the SELECT part of the query
    w=[] #the WHERE part of the query
    WHERE=''

    if viewtype=='mouse':
        FROM=" FROM mice AS m LEFT JOIN housing ON housing.mouse_id=m.id LEFT JOIN cages ON cages.id=housing.cage_id LEFT JOIN lineage ON lineage.child_id=m.id LEFT JOIN mice AS mom ON lineage.mother_id=mom.id LEFT JOIN mice AS dad ON lineage.mother_id=dad.id LEFT JOIN experiments ON experiments.mouse_id=m.id LEFT JOIN lab_members ON experiments.lab_member_id=lab_members.id LEFT JOIN genetics ON genetics.mouse_id=m.id LEFT JOIN genes ON genes.id=genetics.gene_id "
        q.append('housing.currentcage')      
        mousekeys=set(c.keys()).intersection(set(MouseAlias.keys()))
        for key in mousekeys:
            q.append(MouseAlias[key])
            if key in WhereAlias.keys():
                w.append(c[key])
        w=[item for item in w if item is not None]
        if len(w)>0:
            WHERE=' WHERE '+' AND '.join(w)
        query= 'SELECT m.id, '+', '.join(q)
        ORDERBY=" ORDER BY m.name"
        
    elif viewtype=='cage':
        FROM=" FROM cages as c LEFT JOIN care_taker AS ct ON ct.cage_id=c.id LEFT JOIN lab_members ON ct.lab_member_id=lab_members.id "
        cagekeys=set(c.keys()).intersection(set(CageAlias.keys())) 
        if 'residents' in cagekeys: # this prevents a duplicate row in the mysql answer
            FROM+="LEFT JOIN housing as h ON h.cage_id=c.id LEFT JOIN mice as m ON h.mouse_id=m.id LEFT JOIN litters ON litters.cage_id=c.id "
        for key in cagekeys:
            q.append(CageAlias[key])
            w.append(c[key])
        w=[item for item in w if item is not None]
        if len(w)>0:
            WHERE=' WHERE '+' AND '.join(w)
        query= 'SELECT c.id, ' + ', '.join(q)
        ORDERBY=" ORDER BY cagename2"
    query+=FROM+WHERE+ORDERBY
    return db2.execute(query,d)
        


class Ajax:

    @cherrypy.expose
    def refresh(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes an unknown user to the login screen
        article="<thead><tr>"    
        
        #########################   
        #########   CREATE HEADER 
        cols=db.execute("SELECT columns FROM lab_members WHERE name=%s",(username,))[0][0]
        viewtype=db.execute("SELECT viewtype FROM lab_members WHERE name=%s",(username,))[0][0]
        if viewtype is None:
            db.execute("UPDATE lab_members SET viewtype='mouse' WHERE name=%s",(username,))
            viewtype='mouse'
        if cols is None:
            if viewtype=='mouse':
                cols="mousename,,"
            elif viewtype=='cage':
                cols="cagename,,"
        cols=cols.split(',')
        mousecols=getAllMouseColumns()
        cagecols=getAllCageColumns()
        for i in range(0,len(cols)-1,2):
            if (viewtype=='mouse' and cols[i] in mousecols) or (viewtype=='cage' and cols[i] in cagecols):
                if cols[i+1]=='': classs=''
                else: classs="filtered"
                article+="""<th data-header='{0}' class='{2}' filter='{1}'>{3} 
                                <img src='/support/images/drag-handle.png' class='col-handle'>
                                <img class="filterclose_button {2}" onclick="removefilter($(this).parent().attr('data-header'));" src="/support/images/x2.gif">
                            </th>""".format(cols[i],cols[i+1],classs,getPrettyText(cols[i]))     
        article+="</tr></thead><tbody>"
        
        #########################   
        #########   CREATE BODY  
        if cols==['','','']:
            return ''
        columns=[]
        coldict={}
        for i in range(0,len(cols)-1,2):
            columns.append(cols[i])
            c=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in cols[i+1].split('&')]
            if c==[['']]:
                c=None
            coldict[cols[i]]= c
        for key in coldict:
            if coldict[key] is not None:
                for i in range(len(coldict[key])):
                    if coldict[key][i][1]=='Yes':
                        coldict[key][i][1]=1
                    elif coldict[key][i][1]=='No':
                        coldict[key][i][1]=0
        answer=makequery(viewtype,coldict)
        if viewtype=='cage':
            cagesAdded=dict()
            if answer!=[]:
                if 'resident' in answer[0].keys():
                    for i in range(0,len(answer)):
                        entry=answer[i]
                        if entry['cagename2'] not in cagesAdded:
                            cagesAdded[entry['cagename2']]=i
                            entry['residents']=set()
                            if entry['resident'] is not None and entry['currentcage']==1:
                                entry['residents'].add("<span class='resident "+entry['sex']+' '+entry['reserved']+"'><span class='mousename' mouseID='{0}'>".format(entry['mouseID'])+entry['resident']+"</span>"+' ('+getAge(entry['DOB'])+")</span>")
                            if entry['litterDOB'] is not None:
                                entry['residents'].add("<span class='resident'><span class='pl'>PL</span>"+' ('+getAge(entry['litterDOB'])+")</span>")
                        else:
                            oldi=cagesAdded[entry['cagename2']]
                            if entry['resident'] is not None and entry['currentcage']==1:
                                answer[oldi]['residents'].add("<span class='resident "+entry['sex']+' '+entry['reserved']+"'><span class='mousename' mouseID='{0}'>".format(entry['mouseID'])+entry['resident']+"</span>"+' ('+getAge(entry['DOB'])+")</span>")
                            if entry['litterDOB'] is not None:
                                answer[oldi]['residents'].add("<span class='resident'><span class='pl'>PL</span>"+' ('+getAge(entry['litterDOB'])+")</span>")
                    answer=[answer[i] for i in cagesAdded.values()]
                    for entry in answer:
                        if entry['residents'] != set():
                            entry['residents']=', '.join(list(entry['residents']))
                        else:
                            entry['residents']=None
                else:
                    pass
#                    cagesAdded=set()
#                    for i in range(len(answer),0,-1):
#                        entry=answer[i]
#                        if entry['cagename2'] not in cagesAdded:
#                            cagesAdded.add(entry['cagename2'])
#                        else:
#                            del answer[i]
                            
            for entry in answer:
                article+="<tr>"
                for col in columns:
                    if col in getAllCageColumns():
                        if entry[col]==None:
                            entry[col]='-'
                        elif type(entry[col])==type(datetime.datetime.now()):
                            entry[col]=date2str(entry[col])
                        elif entry[col]==0:
                            entry[col]='No'
                        elif entry[col]==1:
                            entry[col]='Yes'
                        if col=='cagenotes':
                            text=html_escape(entry[col])
                            article+="<td class='{0} tooltip' title='{1}'>{2}</td>".format(col,text,text[:20])   #only display the first 20 characters, tooltip the rest
                        else:
                            article+="<td class='{0}'>{1}</td>".format(col,entry[col])
                article+="</tr>"
        else: #if viewtype=='mouse' or if user has no viewtype
        
            #Loop through all entries returned from the mysql query, combining columns that are identical except for genetics
            miceAdded=dict() #this is a dict of mousenames, where the entries are the index in 'answer' that they appear.
            for i in range(0,len(answer)):
                entry=answer[i]
                if entry['mousename'] not in miceAdded:
                    miceAdded[entry['mousename']]=i
                    if 'genename' in entry.keys():
                        if entry['genename'] is not None and entry['zygosity'] is not None:
                            entry['genetics']=set([entry['genename']+entry['zygosity']])
                        else:
                            entry['genetics']=None
                    if 'cagename' in entry.keys():
                        if entry['currentcage']==1:
                            pass
                        else:
                            entry['cagename']=None
                else: #if mouse has already been added to 'miceAdded'
                    oldi=miceAdded[entry['mousename']]
                    if 'cagename' in entry.keys():
                        if answer[i]['currentcage']==1:
                            answer[oldi]['currentcage']=1
                            answer[oldi]['cagename']=answer[i]['cagename']
                    if 'genename' in entry.keys():
                        if entry['genename'] is not None and entry['zygosity'] is not None:
                            answer[oldi]['genetics'].add(entry['genename']+entry['zygosity'])
            answer=[answer[i] for i in miceAdded.values()]
            for entry in answer:
                if 'genetics' in entry.keys():
                    if entry['genetics'] is not None:
                        entry['genetics']=', '.join(list(entry['genetics']))
            if 'genetics' in coldict.keys() and coldict['genetics'] is not None: #if there is a filter for genetics
                for ii in range(len(answer)-1,-1,-1):#this loop will apply the 'genetics' filter and remove items not fulfilling criteria
                    entry=answer[ii]    
                    if entry['genetics'] is None:
                        e=''
                    else:
                        e=entry['genetics'].split(', ')
                    c=coldict['genetics']
                    c2=[] #will look like this: [u'AND', u'PV-Cre+-', u'AND', u'Bgeo/GFP--']
                    for i in range(0,len(c),3):
                        c2.append(c[i][1])
                        c2.append(c[i+1][1]+c[i+2][1])
                    currentbool=True
                    for i in range(0,len(c2),2):
                        newbool= c2[i+1] in e
                        if c2[i]=='AND':
                            currentbool=currentbool and newbool
                        elif c2[i]=='OR':
                            currentbool=currentbool or newbool
                        if c2[i]=='NOT':
                            currentbool=currentbool and not newbool
                    if not currentbool:
                        del answer[ii]
                    
                    
            for entry in answer:
                article+="<tr>"
                for col in columns:
                    if col in getAllMouseColumns():
                        if entry[col]==None:
                            entry[col]='-'
                        elif type(entry[col])==type(datetime.datetime.now()):
                            entry[col]=date2str(entry[col])
                        elif entry[col]==0:
                            entry[col]='No'
                        elif entry[col]==1:
                            entry[col]='Yes'
                        if col=='mousename':
                            article+="<td class='{0}' mouseID={1}>{2}</td>".format(col,entry['id'],entry[col])
                        elif col=='mouse_notes' or col=='reserve_notes':
                            text=html_escape(entry[col])
                            article+="<td class='{0} tooltip' title='{1}'>{2}</td>".format(col,text,text[:20])   #only display the first 20 characters, tooltip the rest
                        else:
                            article+="<td class='{0}'>{1}</td>".format(col,entry[col])
                article+="</tr>"
            article+="</tbody>"
        return article
        
    @cherrypy.expose
    def getFilterForm(self,col): #col is the column information.  it is the name of the column.  eg: DOB
        choicetype='select'
        header="<h1>Select {}</h1>".format(getPrettyText(col))
        if col=='strain':               b=getStrainList();
        elif col=='sex':                b=getSexList();
        elif col=='life_status':        b=getLifeStatusList();
        elif col=='breeding_status':    b=getBreedingStatusList()
        elif col=='reserve_lab_member': b=getLabMemberList()
        elif col=='caretaker':          b=getLabMemberList()
        elif col=='DOB':                choicetype='dates'
        elif col=='DOD':                choicetype='dates'
        elif col=='reserve_date':       choicetype='dates'
        elif col=='date_activated':     choicetype='dates'
        elif col=='date_inactivated':   choicetype='dates'
        elif col=='mousename':          choicetype='textfield'
        elif col=='genotyped':          b=['Yes','No']
        elif col=='cagename':           choicetype='textfield'
        elif col=='mother':             choicetype='textfield'
        elif col=='father':             choicetype='textfield'
        elif col=='cagename2':          choicetype='textfield'
        elif col=='reserve_description':choicetype='textfield'
        elif col=='cagenotes':          choicetype='textfield'
        elif col=='cagegroup':          choicetype='textfield'
        elif col=='mouse_notes':        choicetype='textfield'
        elif col=='location':           choicetype='textfield'
        elif col=='active':             b=['Yes','No']
        elif col=='expectingpl':        b=['Yes','No']
        elif col=='genetics':           choicetype='genetics'
        else: 
            choicetype=None
            header="'{}' doesn't have a filter enabled".format(getPrettyText(col))
            options=''
        if choicetype=='select':
            options="<select name='{}'>".format(col) 
            for i in range(len(b)): options+="""<option value="{0}">{0}</option>""".format(b[i])
            options+="</select><input class='button-link' type='submit'>" 
        elif choicetype=='textfield':
            options="<input type='text' name='{}'><input class='button-link' type='submit'>".format(col)
        elif choicetype=='dates':
            options="<input type= 'date' name='{}'> To <input name='{}' type= 'date'><input class='button-link' type='submit'>".format(col+'1',col+'2')
        elif choicetype=='genetics':
            options=getGeneticFilterForm()+"<input class='button-link' style='float: right;bottom: 10px;right: 10px;white-space: nowrap;' type='submit'>"
        article="<form id='filter' col={}>".format(col)+header+options+"""</form><img class='close_button' src='/support/images/x.gif' onclick="closePopup('.bubble')">"""
        return article
    @cherrypy.expose
    def removefilter(self,col):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        filt=''
        cols=db.execute("SELECT columns FROM lab_members WHERE name=%s",(username,))[0][0]
        if cols is None:
            cols='mousename,,'
        cols=cols.split(',')
        # now find the column of interest and replace its filter with the new filter
        cols[cols.index(col)+1]=filt
        #now convert it back into a string and save it to the database
        cols=','.join(cols)
        db.execute("UPDATE lab_members SET columns=%s WHERE name=%s",(cols,username))
        return(filt)

    @cherrypy.expose
    def setfilter(self,col,filt):
        '''
        Takes a column name and a desired filter, and replaces the column-filter pair in the 'columns' entry in the 'lab_members' table in the database.
        The 'column' entry is used in the 'makequery()' function 
        col - the name of the column we are changing the filter for. eg 'genetics'
        filt - the serialized form the user submits when editing a filter. eg 'logiccomb0=AND&gene0=i-tdTomato&zygosity0=%2B%2B&logiccomb1=AND&gene1=VGAT-Cre&zygosity1=%2B-&logiccomb2=AND&gene2=&zygosity2='
        '''
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        #check if any selection is blank.  If it is, remove filter
        filt2=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in filt.split('&')]
        hasblank=False
        if col=='genetics':
            if len(filt2)==1:
                filt=''
            else:
                if filt2[1][1]=='' or filt2[2][1]=='':
                    hasblank=True
                else:
                    filt='&logiccomb'.join(filt.split('&logiccomb')[:-1]) #gets rid of the last set of blanks
                
            
        else:
            for i in range(len(filt2)):
                if filt2[i][1]=='': #if there is a blank
                    hasblank=True
        if hasblank:
            filt=''
        #take all the users column headers from the database
        cols=db.execute("SELECT columns FROM lab_members WHERE name=%s",(username,))[0][0]
        if cols is None:
            cols='mousename,,'
        cols=cols.split(',')
        # now find the column of interest and replace its filter with the new filter
        cols[cols.index(col)+1]=filt
        #now convert it back into a string and save it to the database
        cols=','.join(cols)
        db.execute("UPDATE lab_members SET columns=%s WHERE name=%s",(cols,username))
        return(filt)
        

        
    @cherrypy.expose 
    def trash(self, name, typ):
        ''' 
        This function permanently deletes a mouse, cage, or PL when called.  
        typ is either 'cage' 'mouse' or 'pl'.
        '''
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        if typ=='mouse': #If we are deleting a mouse
            mouseid=db.execute("SELECT id FROM mice WHERE name=%s",(name,))
            if mouseid==[]: 
                return 'You cannot delete this mouse because it does not exist.'
            else:
                mouseid=mouseid[0][0]                
            owner=db.execute("SELECT name FROM lab_members LEFT JOIN experiments ON lab_members.id=experiments.lab_member_id WHERE mouse_id=%s",(mouseid,))
            if owner==[]: 
                owner=None
            else:
                owner=owner[0][0]
            if owner is not None and owner!=username:
                return "{} cannot be deleted because it is reserved by {}".format(name, owner)
            else:
                db.execute('DELETE FROM mice WHERE id=%s',(mouseid,))
                return "{} has been deleted permanently".format(name)
        elif typ=='cage': #If we are deleting a cage
            cageid=db.execute("SELECT id FROM cages WHERE name=%s",(name,))
            if cageid==[]:
                'You cannot delete this cage because it does not exist.'
            else:
                cageid=cageid[0][0]
            owner=db.execute("SELECT name FROM lab_members LEFT JOIN care_taker ON lab_members.id=care_taker.lab_member_id WHERE cage_id=%s",(cageid,))
            if owner==[]: 
                owner=None
            else:
                owner=owner[0][0]
            if owner is not None and owner!=username:
                return "{} cannot be deleted because it is managed by {}".format(name, owner)
            else:
                db.execute("DELETE FROM housing WHERE cage_id=%s",(cageid,))
                db.execute("DELETE FROM care_taker WHERE cage_id=%s",(cageid,))
                db.execute('DELETE FROM cages WHERE id=%s',(cageid,))
                return "{} has been deleted permanently".format(name)
        elif typ=='pl':
            fields=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in name.split('&')]
            d={i[0]: i[1] for i in fields}
            db.execute("DELETE FROM litters WHERE cage_id=%s AND mother_id=%s AND DOB=%s",(d['cage_id'],d['mother_id'],d['DOB']))
            return "That pup litter has been deleted permanently"
    

        
    @cherrypy.expose 
    def selectColumns(self,columns):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        columns=urllib2.unquote(columns.replace('+',' '))
        c=[[b for b in c.split('=')] for c in columns.split('&')] #list of lists
        cols=[k[0] for k in c]
        cols=",,".join(cols)+",,"
        cols=cols.replace('active,,','active,active=Yes,')
        cols=cols.replace('life_status,,','life_status,life_status=alive,')
        cols=cols.replace('caretaker,,','caretaker,caretaker='+username+',')
        db.execute("UPDATE lab_members SET columns=%s WHERE name=%s",(cols,username))
        return cols

    @cherrypy.expose 
    def pickView(self,viewtype):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        if viewtype=='mouse':
            db.execute("UPDATE lab_members SET viewtype='mouse' WHERE name=%s",(username,))
        elif viewtype=='cage':
            db.execute("UPDATE lab_members SET viewtype='cage' WHERE name=%s",(username,))
        return 'success'
    
    @cherrypy.expose
    def pickColumnsForm(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        else:
            oldcols=db.execute("SELECT columns FROM lab_members WHERE name=%s",(username,))[0][0]
            if oldcols is None:
                oldcols=''
            oldcols=oldcols.split(',')
            oldcols=[oldcols[i] for i in range(0,len(oldcols),2)]

            article="<div style='display: none; background-color:yellow; '>f</div>"
            article+="<form id='selectColumns'>"
            article+="<div style='float:left;   margin-right: 50px; margin-bottom:20px; width:100%'>"
            article+="<table><tbody><tr>"
            article+=   "<th><label>Mouse view</label></th>"
            article+=   "<th><label>Cage view</label></th>"
            article+="<tr><td><fieldset id='mouseview'>"
            cols=getAllMouseColumns()
            for c in cols:
                if c in oldcols:
                    checked='checked'
                else:
                    checked=''
                article+="<label>{0}</label><input name='{1}' type='checkbox' {2}><br>".format(getPrettyText(c),c,checked)
            article+=      "</fieldset></td>"
            article+=      "<td><fieldset id='cageview'>"            
            cols=getAllCageColumns()
            for c in cols:
                if c in oldcols:
                    checked='checked'
                else:
                    checked=''
                article+="<label>{0}</label><input name='{1}' type='checkbox' {2}><br>".format(getPrettyText(c),c,checked)  
            article+=      "</fieldset>"            
            article+="</td></tr></tbody></table>"
            article+="</div><input style='position: absolute; bottom: 10px; right: 10px;' class='button-link' type='submit'></form>"
            article+="""<img class='close_button' src='/support/images/x.gif' onclick="closePopup('.bubble')">"""
            return article
        
        
###############################################################################
#########           CAGE STUFF        #########################################
###############################################################################
    @cherrypy.expose
    def addcageForm(self,cageN,cagename):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        if cagename=='': #if creating new cage
            return getCageForm(cageN=cageN)
        else: #if editing cage
            c=Cage(cagename)
            return getCageForm(c.d,cageN,c.mice,c.litters,getcagehistory(cagename))
        
    @cherrypy.expose
    def addcage(self,data, cagename): 
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        
        data2=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in data.split('&')] #list of lists #data: $('#cage'+i+' form').serialize()
        d={}
        c=Cage(cagename)
        for i in data2:
            if i[1]=='':
                d[i[0]]=None
            elif i[1]=='True' or i[1]=='Yes':
                d[i[0]]=1
            elif i[1]=='False' or i[1]=='No':
                d[i[0]]=0
            else:
                d[i[0]]=i[1] #now in dictionary
        if cagename=='': #if this is creating a new cage
            return c.addToDB(d)
        else:
            if c.d==[]: #if this isn't a real cagename
                return "'{}' isn't a real cage name".format(cagename)
            return c.editOldCage(d)
    @cherrypy.expose
    def refreshcage(self,cageid,cagename):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        c=Cage(cagename)
        return  etree.tostring(getInnerCageForm(c.d, c.mice,c.litters,getcagehistory(cagename)), pretty_print=True)
            
            
            
###############################################################################
#########           MOUSE STUFF       #########################################
###############################################################################
    @cherrypy.expose
    def editmouse(self, data, mouseID):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        data2=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in data.split('&')] #list of lists
        m=Mouse(mouseID)
        d={}
        for i in data2:
            if i[1]=='':
                d[i[0]]=None
            elif i[1]=='True' or i[1]=='Yes':
                d[i[0]]=1
            elif i[1]=='False' or i[1]=='No':
                d[i[0]]=0
            else:
                d[i[0]]=i[1] #now in dictionary
        if mouseID=='': # if this is creating a new mouse
            return m.addToDB(d)
        else:
            answer=m.editOldMouse(d)
            if username=='Mel':
                return answer+' Keep it up, Mel!'
            else:
                return answer
    
    @cherrypy.expose
    def mouseform(self,mouseID):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        if mouseID=='': #if adding new mouse
            return getMouseForm()
        else: #if editing old mouse
            m=Mouse(mouseID)
            return getMouseForm(m.d)
        
    @cherrypy.expose
    def moveMouse(self,mouseID,newcage):
        username=checkPassword()
        
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        m=Mouse(mouseID)
        m.d['name']=m.d['mousename']
        return m.transfer(newcage)+','+etree.tostring(getResident(m.d), pretty_print=True)
            
    @cherrypy.expose
    def removeMouseFromCage(self,mouseID):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        m=Mouse(mouseID)
        return m.removeFromCage()
        
###############################################################################
#########           PL STUFF       ############################################
###############################################################################
    @cherrypy.expose    
    def addPLForm(self,cagename):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        article=""
        article+="""<h1>Add Pup Litter</h1><form id='addPL'><div style="float:left;   margin-right: 50px;">"""
        article+="""<div class="bubbleAlert" style="display: none; background-color:yellow; ">f</div>"""
        article+="<label>Cage name: </label><input type='text' name='cagename' value='{}'><br>".format(cagename)
        article+="<label>Date of Birth:</label> <input type= 'date'  name='DOB' value='{}'><br>".format(date2str(datetime.datetime.now()))
        article+="<label>Mother's name:</label> <input type='text' name='mother'><br>"
        article+="<label>Father's name:</label> <input type='text' name='father'><br>"
        article+="<label>Notes: </label>  <textarea rows='10' cols='30' name='notes'></textarea>"
        article+="""<a class='button-link' onclick="addPL($('#addPL').serialize(),'{}');">Submit</a>""".format(cagename)
        article+="</form>"
        article+="""<img class='close_button' src='/support/images/x.gif' onclick="closePopup('.bubble')"> """
        article+="</div>"
        return article
        
    @cherrypy.expose
    def editplForm(self,plinfo):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        fields=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in plinfo.split('&')]
        d={i[0]: i[1] for i in fields}
        oldplinfo='&oldcage_id={}&oldDOB={}&oldmother_id={}'.format(d['cage_id'],d['DOB'],d['mother_id'])
        d=db2.execute("SELECT l.DOB, l.notes, mom.name AS mother, dad.name AS father, cages.name AS cagename FROM litters AS l LEFT JOIN mice AS mom ON mom.id=mother_id LEFT JOIN mice AS dad ON dad.id=father_id LEFT JOIN cages ON cages.id=l.cage_id WHERE l.cage_id=%s AND l.mother_id=%s AND l.DOB=%s",(d['cage_id'],d['mother_id'],d['DOB']))[0]
        article=""
        article+="""<h1>Edit Pup Litter</h1><form id='editPL'><div style="float:left;   margin-right: 50px;">"""
        article+="""<div class="bubbleAlert" style="display: none; background-color:yellow; ">f</div>"""
        article+="<label>Cage name: </label><input type='text' name='cagename' value='{}'><br>".format(d['cagename'])
        article+="<label>Date of Birth:</label> <input type= 'date'  name='DOB' value='{}'><br>".format(date2str(d['DOB']))
        article+="<label>Mother's name:</label> <input type='text' name='mother' value='{}'><br>".format(d['mother'])
        article+="<label>Father's name:</label> <input type='text' name='father' value='{}'><br>".format(d['father'])
        article+="<label>Notes: </label>  <textarea rows='10' cols='30' name='notes'>"+d['notes']+"</textarea>"
        editpl="editPL($('#editPL').serialize()+'{0}','{1}');".format(oldplinfo,d['cagename'])
        article+="""<a class='button-link' onclick="{0}">Submit</a>""".format(editpl)
        article+="</form>"
        article+="""<img class='close_button' src='/support/images/x.gif' onclick="closePopup('.bubble')"> """
        article+="""<a class='button-link' onclick="{0} separatePLform($('#editPL').serialize());">Separate</a>""".format(editpl)
        article+="</div>"
        return article
    @cherrypy.expose
    def editPL(self,fields):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        fields=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in fields.split('&')]
        d={i[0]: i[1] for i in fields}
        cage_id=db.execute("SELECT id FROM cages WHERE name=%s",(d['cagename'],),commit=False)
        if cage_id==[]:
            return 'The cage you selected does not exist'
        del d['cagename']
        d['cage_id']=cage_id[0][0]
        
        father_id=db.execute("SELECT id FROM mice WHERE name=%s",(d['father'],),commit=False)
        if father_id==[]:
            return 'The father you selected does not exist'
        del d['father']
        d['father_id']=father_id[0][0]
        
        mother_id=db.execute("SELECT id FROM mice WHERE name=%s",(d['mother'],),commit=False)
        if mother_id==[]:
            return 'The mother you selected does not exist'
        del d['mother']
        d['mother_id']=mother_id[0][0]
        db.execute("DELETE FROM litters WHERE cage_id=%s AND mother_id=%s AND DOB=%s",(d['oldcage_id'],d['oldmother_id'],d['oldDOB']))
        del d['oldcage_id']
        del d['oldmother_id']
        del d['oldDOB']
        columns=', '.join(d.keys())
        parameters = ', '.join(['%({0})s'.format(k) for k in d.keys()])
        query = 'INSERT INTO litters ({0}) VALUES ({1})'.format(columns, parameters)
        db.execute(query,d)
        return 'Successfully edited pup litter'
    @cherrypy.expose
    def addPL(self,fields):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
            
            
        fields=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in fields.split('&')]
        d={i[0]: i[1] for i in fields}
        cagename=d['cagename']
        cage_id=db.execute("SELECT id FROM cages WHERE name=%s",(d['cagename'],),commit=False)
        if cage_id==[]:
            return 'The cage you selected does not exist'
        del d['cagename']
        d['cage_id']=cage_id[0][0]
        
        father_id=db.execute("SELECT id FROM mice WHERE name=%s",(d['father'],),commit=False)
        if father_id==[]:
            return 'The father you selected does not exist'
        del d['father']
        d['father_id']=father_id[0][0]
        
        mother_id=db.execute("SELECT id FROM mice WHERE name=%s",(d['mother'],),commit=False)
        if mother_id==[]:
            return 'The mother you selected does not exist'
        del d['mother']
        d['mother_id']=mother_id[0][0]
        columns=', '.join(d.keys())
        parameters = ', '.join(['%({0})s'.format(k) for k in d.keys()])
        query = 'INSERT INTO litters ({0}) VALUES ({1})'.format(columns, parameters)
        db.execute(query,d)
        return 'Successfully added pup litter to {}'.format(cagename)
    @cherrypy.expose
    def separatePLform(self,plinfo):
        fields=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in plinfo.split('&')]
        d={i[0]: i[1] for i in fields}
        article=''
        article+="""<h1>Separate Pup Litter</h1><form id='separatePL'><div style="float:left;   margin-right: 50px;">"""
        article+="""<div class="bubbleAlert" style="display: none; background-color:yellow; ">f</div>"""
        article+="<input type='hidden' name='cagename' value='{}'>".format(d['cagename'])
        article+="<input type='hidden' name='DOB'      value='{}'>".format(d['DOB'])
        article+="<input type='hidden' name='mother'   value='{}'>".format(d['mother'])
        article+="<input type='hidden' name='father'   value='{}'>".format(d['father'])
        article+="<input type='hidden' name='notes'    value='{}'>".format(d['notes'])
        article+="<label>Base name: </label><input type='text' name='basename' value='{}'>".format(d['mother'][0]+'.'+d['DOB'].replace('-','')[2:]+'.')
        article+="<label>Number of males: </label><input type='text'   name='nmales'>"
        article+="<label>Number of females: </label><input type='text'   name='nfemales'>"
        article+="<label>Number of unknowns: </label><input type='text'   name='nunknowns'>"
        article+="""<a class='button-link' onclick="{0}">Submit</a>""".format("separatePL($('#separatePL').serialize());")
        article+="</form>"
        article+="""<img class='close_button' src='/support/images/x.gif' onclick="closePopup('.bubble')"> """
        article+="</div>"
        return article
    @cherrypy.expose
    def separatePL(self,plinfo):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        fields=[[urllib2.unquote(tmp2.replace('+',' ')) for tmp2 in tmp.split('=')] for tmp in plinfo.split('&')]
        d={i[0]: i[1] for i in fields}
        d['life_status']='alive'
        d['genotyped']=0
        d['breeding_status']='virgin'
        d['startDate']=d['DOB']
        cage_id=db.execute("SELECT id FROM cages WHERE name=%s",(d['cagename'],),commit=False)[0][0]
        mother_id=db.execute("SELECT id FROM mice WHERE name=%s",(d['mother'],),commit=False)[0][0]
        if db.execute("SELECT * from litters WHERE cage_id=%s AND mother_id=%s AND DOB=%s",(cage_id,mother_id,d['DOB']))==[]:
            return 'The PL you are trying to separate no longer exists.'
        m=Mouse()
        try:
            d['nmales']=int(d['nmales'])
            d['nfemales']=int(d['nfemales'])
            d['nunknowns']=int(d['nunknowns'])
        except ValueError:
            return 'The number of males and females must be an integer value.'
        i=0
        d['sex']='male'
        for n in range(d['nmales']):
            i+=1
            d['mousename']=d['basename']+str(i)
            while db.execute("SELECT id FROM mice WHERE name=%s",(d['mousename'],),commit=False) != []:
                i+=1
                d['mousename']=d['basename']+str(i)
            m.addToDB(d)
        
        d['sex']='female'
        for n in range(d['nfemales']):
            i+=1
            d['mousename']=d['basename']+str(i)
            while db.execute("SELECT id FROM mice WHERE name=%s",(d['mousename'],),commit=False) != []:
                i+=1
                d['mousename']=d['basename']+str(i)
            m.addToDB(d)
        d['sex']='unknown'
        for n in range(d['nunknowns']):
            i+=1
            d['mousename']=d['basename']+str(i)
            while db.execute("SELECT id FROM mice WHERE name=%s",(d['mousename'],),commit=False) != []:
                i+=1
                d['mousename']=d['basename']+str(i)
            m.addToDB(d)
        db.execute("DELETE FROM litters WHERE cage_id=%s AND mother_id=%s AND DOB=%s",(cage_id,mother_id,d['DOB']))
        return 'Successfully separated pup litter!'
    
        

class Database:
    ajax=Ajax()
    @cherrypy.expose
    def index(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        ###################################################################################################################
        #                                                                                             STYLE AND JAVASCRIPT
        ###################################################################################################################    
        style=""" 
        .filterclose_button:not(.filtered){display:none;}
        .filterclose_button.filtered{
            position: absolute;
            top: 2px;
            right: 2px;
            z-index: 1;
            display:none;}
        
        .header:hover .filterclose_button.filtered{display:block;}

            """
        javascript="""
        
        function separatePLform(plinfo){
            $.post("/database/ajax/separatePLform/",{plinfo:plinfo},function(data){
                $('.bubble').html(data);
               },'text');
        }
        function separatePL(plinfo){
            $.post("/database/ajax/separatePL/",{plinfo:plinfo},function(data){
                if(data=='');
                else{
                    clearTimeout(t);
                    bubbleAlert=$('.bubble').find('.bubbleAlert');
                    bubbleAlert.html(data)
                    bubbleAlert.show();
                    }
                var fadefunc="bubbleAlert.hide('fade', {}, 200);";
                t=setTimeout(fadefunc,2000);
                var cagename=plinfo.split('cagename=')[1].split('&')[0];
                refreshcage(cagename);
               },'text');
        }
        
        function clickedOnMouseName(mouseID){
            $('.bubble').show();
            editmice(mouseID);
        }
        
        $( document ).ready(function(){
        
        
            
            
    
        });
        
        """

        resources= "<style type='text/css'>"+style+"</style>"
        resources+="<link rel='stylesheet' href='/support/css/database.css' type='text/css' />"
        resources+="<link rel='stylesheet' href='/support/css/dragtable.css' type='text/css' />"
        resources+="<script type='text/javascript'>"+javascript+"</script>"
        resources+="<script type='text/javascript' src='/support/javascript/jquery.dragtable.js'></script>"
        resources+="<script type='text/javascript' src='/support/javascript/databaseInterface.js'></script>"
        resources+="<script type='text/javascript' src='/support/javascript/jquery.tablesorter.js'></script> "
        resources+="<link rel='stylesheet' type='text/css' href='/support/thirdparty/tooltipster/css/tooltipster.css' />"
        resources+="<script type='text/javascript' src='/support/thirdparty/tooltipster/js/jquery.tooltipster.js'></script>"
        
        viewtype,cols=db.execute("SELECT viewtype, columns FROM lab_members WHERE name=%s",(username,))[0]
        if viewtype is None:
            viewtype='mouse'
            cols="mousename,,"
        if cols is None:
            cols="mousename,,"
        cols=cols.split(',')
        if viewtype=='mouse':
            c='checked'
        else:
            c=''
        article= ''
        article+="""<div class="onoffswitch" id='viewtype'>
                        <input type="checkbox" name="view" class="onoffswitch-checkbox" id="myonoffswitch" {0}>
                        <label class="onoffswitch-label" for="myonoffswitch">
                            <div class="onoffswitch-inner"></div>
                            <div class="onoffswitch-switch"></div>
                        </label>
                    </div>""".format(c)
        article+="""<table id='db' class="tablesorter"></table>"""
        
        
        rightbar= """<p><a id="editmice" class="button-link getBubbleButton"  style='top:70px;padding:3px 5px;display: block;width: 120px;'">Add Mice</a></p>
                     <p><a id="addcage" class="button-link"  style='top:106px; padding:3px 5px;display: block;width: 120px;'">Add Cage</a></p>
                     <p><a id="pickColumns" class="button-link getBubbleButton"  style='top:142px;padding:3px 5px;display: block;width: 120px;'">Pick Columns</a></p>
                     <p><img id='trashcan' src='/support/images/trash.svg'  style='top:200px; height: 60px;'"></p>"""
        username=checkPassword()

        return glamsTemplate(article, username, resources=resources, rightbar=rightbar)


