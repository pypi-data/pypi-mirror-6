#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = "Camilo A. Ospina A."
__copyright__ = "Copyright 2012-2014, Bogotá, Colombia"
__credits__ = ["Camilo A. Ospina A."]
__license__ = "MIT"
__version__ = "PyTam 0.1"
__maintainer__ = "Camilo A. Ospina A."
__email__ = "camilo.ospinaa@gmail.com"
__status__ = "Testing"

from os import name as osn
class invalid_TWS_Route(Exception):pass
class invalid_TWS_Name(Exception):pass
class invalid_TWS_Password(Exception):pass
class Table_Problem(Exception):pass
class Data_Type(Exception):pass
class invalid_Parameter(Exception):pass

if osn == "posix": # Unix/Linux/MacOS/BSD/etc
    operatingSystem='unixbased'
    s='/'
elif osn in ("nt", "dos", "ce"): # DOS/Windows
    operatingSystem='windows'
    s='\\'    
    
def createTWS(*args): 
    '''
    creteTWS creates a table workspace and allows different ways of use, you can
    choose the one that fits the best your needs.
    
    Method 1:
        By just executing the createTWS method you will get a new
        table workspace called "pytam" with a default password set to
        "pytam", this table workspace will be created on "./" .
        
        eg: createTWS()
        
    Method 2:
        You can specify the location, name and password of the new table
        workspace (always using forward slashes "/" to specify the location).
        if you only specify the location and name of the table workspace the
        password will be sent to blank ("").

        eg1:
            createTWS("/home/user", "TWS_1", "myPassword")
            createTWS("C:/Users/user", "TWS_1", "myPassword")
            
        eg2:
            createTWS("/home/user", "TWS_1")
            createTWS("C:/Users/user", "TWS_1")
            
    Method 3:
        You can specify only the name and password. Using this method the
        table workspace location will be on "./", and just like in the method 2
        if you only specify the name the password will be set blank ("").
        
        eg1:
            createTWS("TWS_1", "myPassword")
            createTWS("TWS_1")
        
    '''
    from subprocess import call
    import os.path
    from gzip import open as gopen    
    
    if len(args)==0:
        route=os.path.abspath('')+s+'pytam'
        if  operatingSystem=='unixbased':            
            if os.path.exists(route): raise invalid_TWS_Route("Table Workspace already exist.")
            route=route.replace(' ', '\\ ')
            command='mkdir %s'%(route)
            command2='mkdir %s'%(route+s+'tables')
            command3='mkdir %s'%(route+s+'tables/logs')
            call(command, shell=True)
            call(command2, shell=True)
            call(command3, shell=True)
            route=route.replace('\\ ', ' ')
        elif operatingSystem=='windows':
            route=os.path.normpath(route)
            if os.path.exists(route): raise invalid_TWS_Route("Table Workspace already exist.")
            command='mkdir %s%s%s'%('"',route,'"')
            command2='mkdir %s%s%s'%('"',route+s+'tables','"')
            command3='mkdir %s%s%s'%('"',route+s+'tables\logs','"')
            call(command, shell=True)
            call(command2, shell=True)
            call(command3, shell=True)
        with gopen(route+s+'_.gz', 'w') as f:
            f.write(_('pytam'))
        with gopen(route+s+'tables'+s+'tables.gz', 'w') as f:
            f.write(b'')
        
    elif len(args)==1:        
        name=args[0]        
        if '/'in name: raise invalid_TWS_Name("Table Workspace name can't contain slashes '/'. ")
        route=route=os.path.abspath('')+s+name
        password=''
        if  operatingSystem=='unixbased':            
            if os.path.exists(route): raise invalid_TWS_Route("Table Workspace already exist.")
            route=route.replace(' ', '\\ ')
            command='mkdir %s'%(route)
            command2='mkdir %s'%(route+s+'tables')
            command3='mkdir %s'%(route+s+'tables/logs')
            call(command, shell=True)
            call(command2, shell=True)
            call(command3, shell=True)
            route=route.replace('\\ ', ' ')
        elif operatingSystem=='windows':
            route=os.path.normpath(route)
            if os.path.exists(route): raise invalid_TWS_Route("Table Workspace already exist.")
            command='mkdir %s%s%s'%('"',route,'"')
            command2='mkdir %s%s%s'%('"',route+s+'tables','"')
            command3='mkdir %s%s%s'%('"',route+s+'tables\logs','"')
            call(command, shell=True)
            call(command2, shell=True)
            call(command3, shell=True)
        with gopen(route+s+'_.gz', 'w') as f:
            f.write(_(password))
        with gopen(route+s+'tables'+s+'tables.gz', 'w') as f:
            f.write(b'')
        
    elif 2<=len(args)<=3:
        if len(args)==3:
            route= args[0]
            name=args[1]
            password=args[2]
            if '/' not in route: raise invalid_TWS_Route("Invalid Route.")
            if '/' in name: raise invalid_TWS_Name("Table Workspace name can't contain slashes '/'. ")
            if '/' in password: raise invalid_TWS_Password("Table Workspace password can't contain slashes '/'. ")
            
        if len(args)==2:        
            if '/'in args[0]:
                route= args[0]
                name=args[1]
                password=''
            else:
                route=os.path.abspath('')
                name=args[0]
                password=args[1]
            if '/' in name: raise invalid_TWS_Name("Table Workspace name can't contain slashes '/'. ")
            if '/' in password: raise invalid_TWS_Password("Table Workspace password can't contain slashes '/'. ")
        
        if  operatingSystem=='unixbased':            
            if not os.path.exists(route):
                raise invalid_TWS_Route("Route for creation doesn't exist.")
            elif os.path.exists(route+s+name):
                raise invalid_TWS_Route("Table Workspace already exist.")        
            route=route+s+name
            route=route.replace(' ', '\\ ')
            command='mkdir %s'%(route)            
            command2='mkdir %s'%(route+s+'tables')
            command3='mkdir %s'%(route+s+'tables/logs')
            call(command, shell=True)
            call(command2, shell=True)
            call(command3, shell=True)
            route=route.replace('\\ ', ' ')
        elif operatingSystem=='windows':
            route=os.path.normpath(route)
            if not os.path.exists(route):
                raise invalid_TWS_Route("Route for creation doesn't exist.")
            elif os.path.exists(route+s+name):
                raise invalid_TWS_Route("Table Workspace already exist.")
            route=route+s+name
            command='mkdir %s%s%s'%('"',route,'"')
            command2='mkdir %s%s%s'%('"',route+s+'tables','"')
            command3='mkdir %s%s%s'%('"',route+s+'tables\logs','"')
            call(command, shell=True)
            call(command2, shell=True)
            call(command3, shell=True)
        with gopen(route+s+'_.gz', 'w') as f:
            f.write(_(password))
        with gopen(route+s+'tables'+s+'tables.gz', 'w') as f:
            f.write(b'')
            
def useTWS(route, password,user=None,logs='disable'):
    '''
    Return an object with the table workspace connection if the TWS exist and the password
    matches with the one given otherwise raises an exception.
    
    eg:
        tws=useTWS("/home/user/TWS1", "1234")
        tws=useTWS("C:/Users/user/TWS1", "1234")
    '''
    from gzip import open as gopen
    
    if operatingSystem=='windows':
        import os
        route=os.path.normpath(route)  
    try:        
        with gopen(route+s+'_.gz', 'r') as f:
            key=__(f.readline())
        if key == password:
            return connection(route,user,logs)
        else: raise invalid_TWS_Password('Wrong password')
    except IOError:
        raise invalid_TWS_Route("Route for connection doesn't exist.")
 
def _(___):
    __= ''.join( [ "%02X" % ord( ____ ) for ____ in ___ ] )
    return str.encode(__)
    
def __(_):
    _=bytes.decode(_)
    _=bytes.fromhex(_)
    try:
        result=bytes.decode(_,encoding='latin1')
    except UnicodeDecodeError:
        result=bytes.decode(_,encoding='utf-8', errors='replace')
    return result    
    
class connection():    
    def __init__(self, route, user=None, logs='disable'):
        ''' Returns the handle of the connection to the table workspace'''  
        self.route=route
        self.tablesR=route+s+'tables'+s
        self.user=user
        self.logs=logs.lower()
        
    def createTable(self, name, columns):
        '''
        createTable allows to create tables into a table workspace, by receiving
        the name of the table and a dictionary with the fields names and data types.
        The possible data types are: 'str', 'char', 'bool', 'float', 'int', 'date' and 'file' 
        To specify the key field this must be preceded by a star "*".
        
        eg:
            tws.createTable('table1',{
                '*id': 'int',
                'name': 'str',
                'lastName':, 'str'       
            })
        
        '''
        from gzip import open as gopen
        from subprocess import call
        import os.path
        
        types=('str', 'char', 'bool', 'float', 'int', 'date', 'file')
        
        if '/' in name: raise Table_Problem("Table name can't contain slashes '/'. ")
        with gopen(self.tablesR+'tables.gz', 'r') as f:
            read=f.readline()
            tables=__(read)
            tables=tables.split()
            if name in tables: raise Table_Problem('Table already exist.')
            
        columns_names= tuple(columns.keys())
        columns_types=tuple(columns.values())
        
        for column_name in columns_names:
            if '/' in column_name: raise Table_Problem("Columns names can't contain slashes '/'. ")            
        for column_type in columns_types:
            if column_type not in types: raise Table_Problem("Columns type '%s' not supported. "%(column_type))   
            
        ftypes1=''
        ftypes2=''
        keys=0
        keypos=-1
        for n in columns_names:
            if n[0]=='*':
                keys+=1
                if keys>1: raise Table_Problem('More than one key found.')
                keypos= columns_names.index(n)
                n= n[1:]
            ftypes1+=(n+' ')
        if keys==0: raise Table_Problem('No key field found.')
        for n in columns_types: ftypes2+=(n+' ')        
        
        route=self.tablesR+name
        if operatingSystem=='unixbased':            
            command='mkdir %s'%(route.replace(' ', '\ '))
            call(command, shell=True)
        elif operatingSystem=='windows':            
            command='mkdir "%s"'%(os.path.normpath(route))
            call(command, shell=True)        
        
        with gopen(self.tablesR+name+s+'types.gz', 'w') as f:
            f.write(_(ftypes1)+b'\n'); f.write(_(ftypes2)+b'\n')
            f.write(_(str(keypos)))
        with gopen(self.tablesR+name+s+'keys.gz', 'w') as f: pass
        with gopen(self.tablesR+name+s+'regs.gz', 'w') as f: pass
        with gopen(self.tablesR+name+s+'num_regs.gz', 'w') as f: f.write(_('0'))
        
        with gopen(self.tablesR+'tables.gz', 'w') as f:
            f.write(read+_(name+' '))
        if self.logs=='enable':
            self.__log('Create table "%s" with the following schema %s'%(name,str(columns)))
            
    def insertInto(self, table, values):
        '''
        insertInto allows to add registries to an specified table by receiving the table name
        and a dictionary with the fields and their corresponding values.
        It's necessary that the key field is present to add a registry, and that all values
        correspond to the data type of the field.
        Date type fields must be on ISO 8601 format.

        eg:
            tws.insertInto('table1',{
                'id':1234,
                'name':'Joe',
                'lastName':'Doe',
                'phone':21312345,
                'work':True,
                'bornDate':'1990-12-1',
                'file1':'/home/user/file1'
                })

        '''
        from gzip import open as gopen

        if table not in self.listTables(): raise Table_Problem("Table not found. ")
        inputFields=list(values.keys())
        with gopen(self.tablesR+s+table+s+'types.gz','r') as f:
            tableFields=__(f.readline()[:-1]).split()
            tableTypes=__(f.readline()[:-1]).split()
            tableKeyPos=int(__(f.readline()))

        if tableFields[tableKeyPos] not in inputFields: raise Table_Problem("No Key Field found.")
        with gopen(self.tablesR+s+table+s+'keys.gz', 'r') as f:
            tableKeys=__(f.readline()).split()
        if str(values[tableFields[tableKeyPos]]) in tableKeys: raise Table_Problem("Key value already exist.")
        for n in inputFields:
            if n not in tableFields: raise Table_Problem("Invalid field '%s', field don't exist."%(n))
        inputValues=list(values.items())

        #'str', 'char', 'bool', 'float', 'int', 'date' and 'file'
        def typeError(n, e=1):
            if e==1:
             raise Data_Type("Invalid data type value for '%s' field."%(n[0]))
            elif e==2:
                raise Data_Type("File '%s' doesn't exist."%(n[1]))
        
        for n in inputValues:
            dataType= tableTypes[tableFields.index(n[0])]
            if dataType=='str':
                try:str(n[1])
                except: typeError(n) 
            elif dataType=='char':
                if len(n[1])!=1:typeError(n)
            elif dataType=='bool':
                if str(type(n[1]))!="<class 'bool'>":typeError(n)
            elif dataType=='float':
                try:float(n[1])
                except: typeError(n)
            elif dataType=='int':
                try:
                    int(n[1])
                    if Dtype(n[1])!='int':typeError(n)
                except: typeError(n)
            elif dataType=='date':
                from datetime import datetime
                m=n[1]
                j=m.split('-')
                if not 3<=len(j)<=7:typeError(n)
                for i in range(len(j)):
                    try: j[i]=int(j[i])
                    except: typeError(n)
                if len(j)==3:
                    try:datetime(j[0],j[1],j[2])
                    except: typeError(n)
                elif len(j)==4:
                    try:datetime(j[0],j[1],j[2],j[3])
                    except: typeError(n)
                elif len(j)==5:
                    try:datetime(j[0],j[1],j[2],j[3],j[4])
                    except: typeError(n)
                elif len(j)==6:
                    try:datetime(j[0],j[1],j[2],j[3],j[4],j[5])
                    except: typeError(n)
                elif len(j)==7:
                    try:datetime(j[0],j[1],j[2],j[3],j[4],j[5],j[6])
                    except: typeError(n)
            elif dataType=='file':
                import os.path
                if not os.path.exists(n[1]):typeError(n,2)

        with gopen(self.tablesR+s+table+s+'keys.gz', 'a') as f:
            f.write(_(str(values[tableFields[tableKeyPos]])+' '))

        reg=''
        for n in tableFields:
            if n in inputFields:
                reg+=str(values[n])+',, '
            else: reg+=',, '
        reg+='end'

        with gopen(self.tablesR+s+table+s+'regs.gz', 'a') as f:
            f.write(_(reg)+b'\n')

        with gopen(self.tablesR+s+table+s+'num_regs.gz', 'r') as f:
            num_regs=int(__(f.readline()))
        with gopen(self.tablesR+s+table+s+'num_regs.gz', 'w') as f:
            f.write(_(str(num_regs+1)))

        if self.logs=='enable':
            self.__log('Added a registry into table "%s" with id (%s,%s)'%(table,str(values[tableFields[tableKeyPos]]),tableTypes[tableKeyPos]))


    def __getRegs(self,table):
        '''
        __getRegs is a hidden method that returns all registries from a given table.

        '''
        from gzip import open as gopen

        if table not in self.listTables(): raise Table_Problem("Table not found. ")
        with gopen(self.tablesR+s+table+s+'types.gz','r') as f:
            tableFields=__(f.readline()[:-1]).split()
            tableTypes=__(f.readline()[:-1]).split()
            tableKeyPos=int(__(f.readline()))

        regs=[]
        if self.numRegs(table)==0:return (regs, tableFields,tableTypes,tableKeyPos)

        with gopen(self.tablesR+s+table+s+'num_regs.gz', 'r') as f:
            num_regs=int(__(f.readline()))

        #'str', 'char', 'bool', 'float', 'int', 'date' and 'file'
        with gopen(self.tablesR+s+table+s+'regs.gz', 'r') as f:
            for n in range(num_regs):
                reg=[]
                singleReg=__(f.readline()[:-1]).split(',, ')[:-1]
                for i,j in zip(singleReg,tableTypes):
                    if j=='str': reg.append(i)
                    elif j=='char':reg.append(i)
                    elif j=='bool':
                        if i=='True':reg.append(True)
                        elif i=='False':reg.append(False)
                    elif j=='float': reg.append(float(i))
                    elif j=='int': reg.append(int(i))
                    elif j=='file': reg.append(i)
                    elif j=='date':
                        from datetime import datetime
                        m=i.split('-')
                        for n2 in range(len(m)):
                            m[n2]=int(m[n2])                     
                        if len(m)==3:reg.append(datetime(m[0],m[1],m[2]))
                        elif len(m)==4:reg.append(datetime(m[0],m[1],m[2],m[3]))                            
                        elif len(m)==5:reg.append(datetime(m[0],m[1],m[2],m[3],m[4]))
                        elif len(m)==6:reg.append(datetime(m[0],m[1],m[2],m[3],m[4],m[5]))
                        elif len(m)==7:reg.append(datetime(m[0],m[1],m[2],m[3],m[4],m[5],m[6]))
                regs.append(reg)
        return (regs, tableFields,tableTypes,tableKeyPos)

    def getSchema(self,table):
        '''
        getSchema returns the schema of an existing table.
        eg:
            tws.getSchema('table1')
        '''
        from gzip import open as gopen

        if table not in self.listTables(): raise Table_Problem("Table not found. ")
        with gopen(self.tablesR+s+table+s+'types.gz','r') as f:
            tableFields=__(f.readline()[:-1]).split()
            tableTypes=__(f.readline()[:-1]).split()
            tableKeyPos=int(__(f.readline()))
        info=[]
        for i,j in zip(tableFields,tableTypes):
            if i == tableFields[tableKeyPos]:
                info.append(('*'+i,j))
            else:info.append((i,j))
        return info

    def numRegs(self,table):
        '''
        numRegs return the number of existing registries on a given table.
        eg:
            tws.numRegs('table1')

        '''
        from gzip import open as gopen

        if table not in self.listTables(): raise Table_Problem("Table not found. ")
        with gopen(self.tablesR+s+table+s+'num_regs.gz', 'r') as f:
            num_regs=int(__(f.readline()))
        return num_regs

    def fetchAll(self, *args):
        '''
        fetchAll returns all registries from a table according to a set of filters, default
        filter is None which return all registries from the given table.

        eg1:
            tws.fetchAll('table1')
        eg2:
            tws.fetchAll('table1', {'id':1})
        eg3:
            tws.fetchAll('table1', {'name':'name1', 'lastname':'lastName1'})

        Registries order by an specific field ('d' is descending and 'a' is ascending)

        eg4: 
            tws.fetchAll('table1','name')
        eg5:
            tws.fetchAll('table1','name','d')
        eg6:

            tws.fetchAll('table1', {'name':'name1'}, 'age','d')
            this get all registries from table1 which name is 'name1' in a descending order by age.

        '''
        pTypes=[]

        for n in args:pTypes.append(Dtype(n))
        if pTypes not in (['str'],['str','dict'],['str','str'],['str','dict','str'],['str','str','str'],['str','dict','str','str']):
            raise invalid_Parameter('One or more parametes are wrong')
        
        if len(args)==1:
            table=args[0]
            filters=None
            orderBy=None
            order='a'

        if len(args)==2:
            table=args[0]
            if Dtype(args[1])=='dict':
                filters=args[1]
                orderBy=None
                order='a'
            if Dtype(args[1])=='str':
                filters={}
                orderBy=args[1]
                order='a'

        if pTypes==['str','dict','str']:
            table=args[0]
            filters=args[1]
            orderBy=args[2]
            order='a'

        if pTypes==['str','str','str']:
            table=args[0]
            orderBy=args[1]
            order=args[2]
            filters={}

        if len(args)==4:
            table=args[0]
            filters=args[1]
            orderBy=args[2]
            order=args[3]

        getRegsReturn=self.__getRegs(table)
        regs,tableFields,tableTypes=getRegsReturn[0],getRegsReturn[1],getRegsReturn[2]
        tableKeyPos=getRegsReturn[3]

        if filters is None:return regs
        inputFields=list(filters.keys())

        for n in inputFields:
            if n not in tableFields: raise Table_Problem("Invalid field '%s', field don't exist."%(n))
        inputValues=list(filters.items())

        #'str', 'char', 'bool', 'float', 'int', 'date' and 'file'
        def typeError(n, e=1):
            if e==1:
             raise Data_Type("Invalid data type value for '%s' field."%(n[0]))
            elif e==2:
                raise Data_Type("File '%s' doesn't exist."%(n[1]))

        for n in inputValues:
            dataType= tableTypes[tableFields.index(n[0])]
            if dataType=='str' or dataType=='file':
                try:str(n[1])
                except: typeError(n) 
            elif dataType=='char':
                if len(n[1])!=1:typeError(n)
            elif dataType=='bool':
                if str(type(n[1]))!="<class 'bool'>":typeError(n)
            elif dataType=='float':
                try:float(n[1])
                except: typeError(n)
            elif dataType=='int':
                try:int(n[1])
                except: typeError(n)
            elif dataType=='date':
                from datetime import datetime
                m=n[1]
                j=m.split('-')
                if not 3<=len(j)<=7:typeError(n)
                for i in range(len(j)):
                    try: j[i]=int(j[i])
                    except: typeError(n)
                if len(j)==3:
                    try:datetime(j[0],j[1],j[2])
                    except: typeError(n)
                elif len(j)==4:
                    try:datetime(j[0],j[1],j[2],j[3])
                    except: typeError(n)
                elif len(j)==5:
                    try:datetime(j[0],j[1],j[2],j[3],j[4])
                    except: typeError(n)
                elif len(j)==6:
                    try:datetime(j[0],j[1],j[2],j[3],j[4],j[5])
                    except: typeError(n)
                elif len(j)==7:
                    try:datetime(j[0],j[1],j[2],j[3],j[4],j[5],j[6])
                    except: typeError(n)

        regsToRemove=[]

        if tableFields[tableKeyPos] in inputFields and len(filters.keys())==1:
            keyValue=filters[tableFields[tableKeyPos]]
            dataType=tableTypes[tableKeyPos]
            #'str', 'char', 'bool', 'float', 'int', 'date' and 'file'
            if dataType=='date':
                from datetime import datetime
                j=keyValue.split('-')
                for i in range(len(j)):j[i]=int(j[i])
                if len(j)==3:keyValue=datetime(j[0],j[1],j[2])
                elif len(j)==4:keyValue=datetime(j[0],j[1],j[2],j[3])
                elif len(j)==5:keyValue=datetime(j[0],j[1],j[2],j[3],j[4])
                elif len(j)==6:keyValue=datetime(j[0],j[1],j[2],j[3],j[4],j[5])
                elif len(j)==7:keyValue=datetime(j[0],j[1],j[2],j[3],j[4],j[5],j[6])
                
            for reg in range(len(regs)):
                if regs[reg][tableKeyPos]!=keyValue:regsToRemove.append(reg)
        else:
            for reg in range(len(regs)):                


                for n in inputValues:
                    dataType=tableTypes[tableFields.index(n[0])]
                    if dataType=='date':
                        from datetime import datetime
                        keyValue=n[1]
                        j=keyValue.split('-')
                        for i in range(len(j)):j[i]=int(j[i])
                        if len(j)==3:keyValue=datetime(j[0],j[1],j[2])
                        elif len(j)==4:keyValue=datetime(j[0],j[1],j[2],j[3])
                        elif len(j)==5:keyValue=datetime(j[0],j[1],j[2],j[3],j[4])
                        elif len(j)==6:keyValue=datetime(j[0],j[1],j[2],j[3],j[4],j[5])
                        elif len(j)==7:keyValue=datetime(j[0],j[1],j[2],j[3],j[4],j[5],j[6])
                        if regs[reg][tableFields.index(n[0])]!=keyValue:
                            regsToRemove.append(reg)
                            break

                    if regs[reg][tableFields.index(n[0])]!=n[1]:
                        regsToRemove.append(reg)
                        break

        tempRegs=[]
        for n in regsToRemove:
            tempRegs.append(regs[n])
        for reg in tempRegs:
            regs.remove(reg)
        if orderBy is None:return regs
        if orderBy not in tableFields:raise Table_Problem("Invalid field '%s', field don't exist."%(orderBy))
        orderBy=tableFields.index(orderBy)
        if regs==[]: return regs
        if order!='d':tree=BinaryTree()            
        else:tree=BinaryTree('d') 
        for reg in regs: tree.insert(reg,orderBy)
        return tree.inorder(tree.root)

    def deleteFrom(self, table, keyvalue):
        '''
        deleteFrom, deletes a registry from a table, given the key value of the registry
        to delete.
        eg:
            tws.deleteFrom('table1','id1')
        '''
        if table not in self.listTables(): raise Table_Problem("Table not found. ")
        from gzip import open as gopen
        with gopen(self.tablesR+s+table+s+'keys.gz', 'r') as f:
            keys=__(f.readline()).split()

        if keys==[]: return False
        keysToWrite=keys[:]

        for n in self.getSchema(table):
            if n[0][0]=='*':dataType=n[1]

        if dataType=='int':
            for n in range(len(keys)):                
                keys[n]=int(keys[n])
        if dataType=='float':
            for n in range(len(keys)):                
                keys[n]=float(keys[n])
        if dataType=='bool':
            for n in range(len(keys)):
                if keys[n]=='True':keys[n]=True
                if keys[n]=='False':keys[n]=False

        regToDel=None
        for n in range(len(keys)):
            if keys[n]==keyvalue:regToDel=n

        if regToDel is None: return False

        regs=[]
        with gopen(self.tablesR+s+table+s+'regs.gz', 'r') as f:
            for n in range(len(keys)):
                reg=f.readline()
                if n!= regToDel:                    
                    regs.append(reg)
        with gopen(self.tablesR+s+table+s+'regs.gz', 'w') as f:
            for n in regs: f.write(n)
        newNumRegs=_(str(self.numRegs(table)-1))
        with gopen(self.tablesR+s+table+s+'num_regs.gz', 'w') as f:
            f.write(newNumRegs)

        strKeys=''
        for n in range(len(keysToWrite)):
            if n!= regToDel: strKeys+= keysToWrite[n]+' '

        with gopen(self.tablesR+s+table+s+'keys.gz', 'w') as f:
            f.write(_(strKeys))
        if self.logs=='enable':
            self.__log('Removed registry from table "%s" with id (%s,%s)'%(table,str(keyvalue),Dtype(keyvalue)))

        return True


    def listTables(self):
        '''
        Return the exiting tables on the Table Workspace.
        eg:
            tws.listTables()
        '''
        from gzip import open as gopen
        with gopen(self.tablesR+'tables.gz', 'r') as f:
            tables=__(f.readline()).split()           
        return tables

    def updateFrom(self, table, keyvalue, values):
        '''
        updateFrom allows to modify data from an existing registry. It works by receiving
        the name of the table in which is located the registry, the Key Value of the registry
        and finally a dictionary with the fields and values to modify.

        eg:
            tws.updateFrom('table1', 'id1', {'name':'newName', 'lastname':'newLastname'})

        '''
        if table not in self.listTables(): raise Table_Problem("Table not found. ")
        from gzip import open as gopen

        inputFields=list(values.keys())
        with gopen(self.tablesR+s+table+s+'types.gz','r') as f:
            tableFields=__(f.readline()[:-1]).split()
            tableTypes=__(f.readline()[:-1]).split()
            tableKeyPos=int(__(f.readline()))

        with gopen(self.tablesR+s+table+s+'keys.gz', 'r') as f:
            tableKeys=__(f.readline()).split()
        keychange=None
        try:
            if str(values[tableFields[tableKeyPos]]) in tableKeys: raise Table_Problem("Key value already exist.")
            else: keychange=str(values[tableFields[tableKeyPos]])
        except KeyError:pass
        for n in inputFields:
            if n not in tableFields: raise Table_Problem("Invalid field '%s', field don't exist."%(n))
        inputValues=list(values.items())

        def typeError(n, e=1):
            if e==1:
             raise Data_Type("Invalid data type value for '%s' field."%(n[0]))
            elif e==2:
                raise Data_Type("File '%s' doesn't exist."%(n[1]))
        
        for n in inputValues:
            dataType= tableTypes[tableFields.index(n[0])]
            if dataType=='str':
                try:str(n[1])
                except: typeError(n) 
            elif dataType=='char':
                if len(n[1])!=1:typeError(n)
            elif dataType=='bool':
                if str(type(n[1]))!="<class 'bool'>":typeError(n)
            elif dataType=='float':
                try:float(n[1])
                except: typeError(n)
            elif dataType=='int':
                try:
                    int(n[1])
                    if Dtype(n[1])!='int':typeError(n)
                except: typeError(n)
            elif dataType=='date':
                from datetime import datetime
                m=n[1]
                j=m.split('-')
                if not 3<=len(j)<=7:typeError(n)
                for i in range(len(j)):
                    try: j[i]=int(j[i])
                    except: typeError(n)
                if len(j)==3:
                    try:datetime(j[0],j[1],j[2])
                    except: typeError(n)
                elif len(j)==4:
                    try:datetime(j[0],j[1],j[2],j[3])
                    except: typeError(n)
                elif len(j)==5:
                    try:datetime(j[0],j[1],j[2],j[3],j[4])
                    except: typeError(n)
                elif len(j)==6:
                    try:datetime(j[0],j[1],j[2],j[3],j[4],j[5])
                    except: typeError(n)
                elif len(j)==7:
                    try:datetime(j[0],j[1],j[2],j[3],j[4],j[5],j[6])
                    except: typeError(n)
            elif dataType=='file':
                import os.path
                if not os.path.exists(n[1]):typeError(n,2)

        with gopen(self.tablesR+s+table+s+'keys.gz', 'r') as f:
            keys=__(f.readline()).split()

        if keys==[]:return False

        keysToWrite=keys[:]

        for n in self.getSchema(table):
            if n[0][0]=='*':dataType=n[1]

        if dataType=='int':
            for n in range(len(keys)):                
                keys[n]=int(keys[n])
        if dataType=='float':
            for n in range(len(keys)):                
                keys[n]=float(keys[n])
        if dataType=='bool':
            for n in range(len(keys)):
                if keys[n]=='True':keys[n]=True
                if keys[n]=='False':keys[n]=False

        regToUpdate=None
        for n in range(len(keys)):
            if keys[n]==keyvalue:regToUpdate=n

        if regToUpdate is None:return False

        newRegs=[]

        with gopen(self.tablesR+s+table+s+'regs.gz', 'r') as f:
            for n in range(self.numRegs(table)):
                if n != regToUpdate: newRegs.append(f.readline())
                else:
                    reg=__(f.readline()[:-1]).split(',, ')[:-1]
                    for i in inputValues:
                        reg[tableFields.index(i[0])]=str(i[1])

                    newReg=''
                    for n in reg:
                        if n!='':
                            newReg+=n+',, '
                        else: newReg+=',, '

                    newReg+='end'
                    newRegs.append(_(newReg)+b'\n')
        with gopen(self.tablesR+s+table+s+'regs.gz', 'w') as f:
            for reg in newRegs: f.write(reg)

        if keychange is not None:
            newKeys=keysToWrite[:regToUpdate]+[keychange]+keysToWrite[regToUpdate+1:]
            keys=''
            for n in newKeys:keys+=n+' '

            with gopen(self.tablesR+s+table+s+'keys.gz', 'w') as f:
                f.write(_(keys))
        if self.logs=='enable':
            self.__log('Updated registry with id (%s,%s) from table "%s"'%(str(keyvalue),tableTypes[tableKeyPos],table))
        return True

    def dropData(self,table):
        '''
        dropData deletes all registries from a given table.
        eg:
            tws.dropData('table1')
        '''
        if table not in self.listTables(): raise Table_Problem("Table not found. ")
        from gzip import open as gopen
        try:
            with gopen(self.tablesR+s+table+s+'regs.gz','w') as f: f.write(b'')
            with gopen(self.tablesR+s+table+s+'keys.gz','w') as f: f.write(b'')
            with gopen(self.tablesR+s+table+s+'num_regs.gz','w') as f: f.write(_('0'))
            if self.logs=='enable':
                self.log('Cleared data from table "%s"'%(table))
            return True
        except Exception: return False

    def dropTable(self,table):
        '''
        dropTable deletes a given table that contains no registries.
        eg:
            tws.dropTable('table1')
        '''
        if table not in self.listTables(): raise Table_Problem("Table not found.")
        if self.numRegs(table)!=0:raise Table_Problem("Tables with data can't be deleted")
        from subprocess import call
        if operatingSystem=='windows':
            command='del /q "%s"'%(self.tablesR+s+table)
            try:
                call(command, shell=True)
                command='rd /q "%s"'%(self.tablesR+s+table)
                call(command, shell=True)
            except Exception: return False
        elif operatingSystem=='unixbased':
            command='rm -r "%s"'%(self.tablesR+s+table)
            try:
                call(command, shell=True)
            except Exception: return False
        
        from gzip import open as gopen
        with gopen(self.tablesR+s+'tables.gz','r') as f:
            newTables=__(f.readline()).split()
            newTables.remove(table)
        newTablesStr=''
        for n in newTables:newTablesStr+=n+' '
        with gopen(self.tablesR+s+'tables.gz','w') as f:f.write(_(newTablesStr))
        if self.logs=='enable':
            self.__log('Deleted table "%s"'%(table))
        return True

    def match(self, keyvalue, tables):
        '''
        match return all registries that matches between different tables given one key value.
        eg:
            tws.match('id1', ['table1', 'table2', 'table3'])
        '''
        for table in tables:
            if table not in self.listTables(): raise Table_Problem('Table "%s" not found.'%(table))
        keysTypes=[]
        for table in tables:
            schema=self.getSchema(table)
            for field in schema:
                if field[0][0]=='*':keysTypes.append(field[1])

        for n in range(len(keysTypes)):
            if keysTypes[n]!=keysTypes[0]:raise Data_Type('Invalid data type "%s" for key field in table "%s"'\
                                                    %(keysTypes[n],tables[n]))

        keysFields=[]
        for table in tables:
            schema=self.getSchema(table)
            for field in schema:
                if field[0][0]=='*':keysFields.append(field[0][1:])
        res=[]
        for n in range(len(tables)):
            reg=self.fetchAll(tables[n],{keysFields[n]:keyvalue})
            if reg==[]: res.append(None)
            else: res.append(reg[0])

        return res

    def __log(self, action):
        from datetime import date
        with open(self.tablesR+s+'logs'+s+str(date.today())+'.log','a') as f:
            f.write(self.user+': '+action+'\n')

class Node():
    def __init__(self,left=None,right=None,p=None):
        self.key=None
        self.left=left
        self.right=right
        self.p=p

class BinaryTree():
    def __init__(self, order='a'):
        self.root=Node()
        self.order=order
        self.res=[]   

    def insert(self,reg,pos):
        z=Node()
        z.reg=reg
        z.key=z.reg[pos]
        if Dtype(z.key)=='str':z.key=z.key.lower()
        y=None
        x=self.root
        if(x.key==None):self.root=z
        elif self.order=='a':
            while(x!=None):
                y=x
                if(z.key<x.key):x=x.left
                else:x=x.right
            z.p=y
            if y==None:self.root=z
            elif z.key<y.key:y.left=z
            else: y.right=z
        elif self.order=='d':
            while(x!=None):
                y=x
                if(z.key>x.key):x=x.left
                else:x=x.right
            z.p=y
            if y==None:self.root=z
            elif z.key>y.key:y.left=z
            else: y.right=z
    
    def inorder(self,x):        
        if(x!=None):
            self.inorder(x.left)
            self.res.append(x.reg)
            self.inorder(x.right)
        return self.res

def Dtype(v):return str(type(v)).split("'")[1]
