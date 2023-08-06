Copyright (c) <2012-2014, Bogotá, Colombia>
<Camilo A. Ospina A. camilo.ospinaa@gmail.com >

===============================================================================
DESCRIPTION
===============================================================================
PyTam is a single module that allows python3 to manipulate databases of
its own. It works for Linux, Mac and Windows.
It can create, delete, update, fetch, match registries and much more. It is not
intended to be a SQL dbm but a python data persistance module that allows managing
data in an efficent way, with more levels of security than other python's
persistance libraries.

Note: It Runs On ANDROID!!!! with QPython 3

If help is needed you can contact me at:
	camilo.ospinaa@gmail.com

I will not write any code for you, but I can show you what you can do with this
powerful library.

===============================================================================
USAGE EXAMPLE
===============================================================================

from pytam.pytam import *

createTWS("/home/user/","DB", "123") #Create DataBase
tws=useTWS('/home/user/DB', '123', 'UserNameForLogs', 'enable') #Connect to DB

tws.createTable('people',{ # Create Table
                '*id': 'int',
                'name': 'str',
                'lastName': 'str'       
            })

tws.insertInto('people',{    #Add Registry to DB
                'id':0,
                'name':'Joe',
                'lastName':'Doe'
                })

PeopleObtained=tws.fetchAll('people', {'id':0}) # Search by Key Field

PeopleObtained=tws.fetchAll('people', {'name:Joe', 'lastName':'Doe'}) # Search by various fields

=====================================================================================

!!! And a lot more you can do with PyTam !!! :)


===============================================================================
LICENSE
===============================================================================
MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
