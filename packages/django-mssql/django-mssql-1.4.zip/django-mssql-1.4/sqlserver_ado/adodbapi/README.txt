Project
-------
adodbapi

A Python DB-API 2.0 (PEP-249) module that makes it easy to use Microsoft ADO 
for connecting with databases and other data sources
using either CPython or IronPython.

Home page: <http://sourceforge.net/projects/adodbapi>

Features:
* 100% DB-API 2.0 (PEP-249) compliant (including most extensions and recommendations).
* Includes pyunit testcases that describe how to use the module.  
* Fully implemented in Python. -- runs in Python 2.5+ Python 3.0+ and IronPython 2.6+
* Licensed under the LGPL license, which means that it can be used freely even in commercial programs subject to certain restrictions. 
* Includes SERVER and REMOTE modules so that a Windows proxy can serve ADO databases to a Linux client using PyRO.
* The user can choose between paramstyles: 'qmark' 'named' 'format'
* Supports data retrieval by column name e.g.:
  for row in myCurser.execute("select name,age from students"):
     print("Student", row.name, "is", row.age, "years old.")
* Supports user-definable system-to-Python data conversion functions (selected by ADO data type, or by column)

Prerequisites:
* C Python 2.5 or higher
 and pywin32 (Mark Hammond's python for windows extensions.)
or
 Iron Python 2.6 or higher.  (works in IPy2.0 for all data types except BUFFER)

Installation:
* (C-Python on Windows): Download pywin32 from http://sf.net/projects/pywin32 and install from .msi (adodbapi is included)
* ((to use Windows as a server, also download and install Pyro4 (requires Python 2.6 or later))) https://pypi.python.org/pypi/Pyro4
* (IronPython on Windows): Download adodbapi from http://sf.net/projects/adodbapi.  Unpack the zip.
     Open a command window as an administrator. CD to the folder containing the unzipped files.
     Run "setup.py install" using the IronPython of your choice.
* (Linux, as a client): download and install from PyPi: "pip install adodbapi Pyro4"
*** NOTE: Pyro4 starting with version 2.20 uses the "serpent" serializer by default.  It _will_ _not_ _work_ to
*** transmit decimal or datetime data items. Remote ado users will have to switch back to the pickle serializer by:
*** SET PYRO_SERIALIZER=pickle
*** (or on Linux)  export PYRO_SERIALIZER=pickle


NOTE: ...........
If you do not like the new default operation of returning Numeric columns as decimal.Decimal,
you can select other options by the user defined conversion feature. 
Try:
        adodbapi.apibase.variantConversions[adodbapi.ado_consts.adNumeric] = adodbapi.apibase.cvtString
or:
        adodbapi.apibase.variantConversions[adodbapi.ado_consts.adNumeric] = adodbapi.apibase.cvtFloat
or:
        adodbapi.apibase.variantConversions[adodbapi.ado_consts.adNumeric] = write_your_own_convertion_function
............
whats new in version 2.5
   Remote module: (works on Linux!) allows a Windows computer to serve ADO databases via PyRO
   Server module: PyRO server for ADO.  Run using a command like= C:>python -m adodbapi.server
   (server has simple connection string macros: is64bit, getuser, sql_provider, auto_security)
   Brief documentation included.  See adodbapi/examples folder adodbapi.rtf
   Vastly refactored. Data conversion things have been moved to the new adodbapi.apibase module.
   Many former module-level attributes are now class attributes. (Should be more thread-safe)
   Connection objects are now context managers for transactions and will commit or rollback.
   Cursor objects are context managers and will automatically close themselves.
   Autocommit can be switched on and off.
   Keyword and positional arguments on the connect() method work as documented in PEP 249.
   Keyword arguments from the connect call can be formatted into the connection string.
   New keyword arguments defined, such as: autocommit, paramstyle, remote_proxy, remote_port.
  *** Breaking change: variantConversion lookups are simplified: the following will raise KeyError:
         oldconverter=adodbapi.variantConversions[adodbapi.adoStringTypes]
      Refactor as: oldconverter=adodbapi.variantConversions[adodbapi.adoStringTypes[0]]

As of version 2.5.0e08 -- you may use a paramstyle of 'auto' which is a combination of 'qmark' and 'named', and
  will select between them based on whether the parameters are passed in a dictionary ('named') or not ('qmark').
   New connection method conn.get_table_names() --> list of names of tables in database
Whats new in version 2.4.3
   Extensively reworked test folder (easier to test Python 3.3) creates and uses temporary folder
   Bug Fix for data type adGUID (from Allan "alkamo")
   Bug Fix for odd-length BINARY objects (from Pawel Jasinski) [also reduces traffic to server]
   new module adodbapi.is64bit:  is64bit.Python() --> boolean    is64bit.os() --> boolean
   new improved /examples folder showing SQL used for ACCESS db and Excel .xls files.
   *** Support warning *** this will be the last version supporting Python 2.3 and 2.4 and IronPython 2.7.1 ***

Whats new in version 2.4.0
1. The result of fetchall() and fetchmany() will be an object which emulates a sequence of sequences.
  The result of fetchone() will be an object which emulates a sequence.
  [This eliminates creating a tuple of return values]
  Also the data are not fetched and converted to Python data types until actually referred to, therefore...
2. Data can be retrieved from the result sets using the column name (as well as the number).
   >>> cs = someConnection.cursor()
   >>> cs.execute('select name, rank, serialNumber from soldiers')
   >>> rows = cs.fetchall()
   >>> for soldier in rows:
   >>>    print soldier.name, soldier['rank'], soldier[2]
   Fred Flintstone private 333-33-3333
   Barny Rubble sergeant 123-45-6789
3. User defined conversions can be applied at the column level from the 'fetch' object:
        (continuing the above example)...
   >>> upcaseConverter=lambda aStringField: aStringField.upper()
   >>> # now use a single column converter
   >>> rows.converters[0] = upcaseConverter  # convert first column as upper case
   >>> for soldier in rows:
   >>>        print soldier.name, soldier.rank
   FRED FLINTSTONE private
   BARNY RUBBLE sergeant
4. Data may be retrieved by a TWO DIMENSIONAL "extended slicing":
   >>> cs.execute('select name, rank, serialNumber from soldiers')
   >>> rows = cs.fetchall()
   >>> print rows[1,2]
   123-45-6789
   >>> print rows[0,'name']
   Fred Flintstone

Whats new in version 2.3.0    # note: breaking changes and default changes!
  This version is all about django support.  There are two hoped-for targets:
    ... A) MS SQL database connections for mainstream django.
    ... B) running django on IronPython
   Thanks to Adam Vandenberg for the django modifications. 

   The changes are:
1. the ado constants are moved into their own module: ado_consts
      This may break some old code, but Adam did it on his version and I like the improvement in readability.
      Also, you get better documentation of some results, like convertion of MS data type codes to strings:
       >>> import adodbapi.ado_consts as ado_consts
       >>> ado_consts.adTypeNames[202]
       'adVarWChar'
       >>> ado_consts.adTypeNames[cursr.description[0][1]]
       'adWChar'
  ** deprecation warning: access to these constants as adodbapi.ad* will be removed in the future **

2. will now default to client-side cursors. To get the old default, use something like:
      adodbapi.adodbapi.defaultCursorLocation = ado_consts.adUseServer  
  ** change in default warning **

3. Added ability to change paramstyle on the connection or the cursor:  (An extension to the db api)
    Possible values for paramstyle are: 'qmark', 'named', 'format'. The default remains 'qmark'.
    (SQL language in '%s' format or ':namedParameter' format will be converted to '?' internally.)
    when 'named' format is used, the parameters must be in a dict, rather than a sequence.
       >>>c = adodbapi.connect('someConnectionString',timeout=30)
       >>>c.paramstyle = 'named'
       >>>cs = c.cursor()
       >>>cs.execute('select * from sometable where firstname = :aname and age = :hisage' , {'aname':'Fred','hisage':35})
  ** new extension feature **

4. Added abality to change the default paramstyle for adodbapi: (for django)
    >>> import adodbapi as Database
    >>> Database.paramstyle = 'format'
 ** new extension feature **
  
Whats new in version 2.2.7
1. Does not automagically change to mx.DateTime when mx package is installed. (This by popular demand.)
   to get results in  mx.DateTime format, use:
      adodbapi.adodbapi.dateconverter =  adodbapi.adodbapi.mxDateTimeConverter
2. implements cursor.next()

Whats new in version 2.2.6
1. Actually works in Python 3.0 (using pywin32 212.6) after running thru 2to3
2. RESTRICTION: Python Time (as opposed to datetime.datetime, which is the default) may return
     incorrect results due to daylight time bugs. To avoid this problem, do not use adodbapi.pythonTimeConverter. 
3. The python time converter test has been loosened so that it will pass in any time zone.
4. Several improvements in the test routines, including alteration of dbapi20 for Python 3.0 compatibility.
   (Some requirements of PEP249 are incompatible with Python 3.0)

Whats new in version 2.2.5
1. Exception definition cleanups for for Python 3.0 readiness [Mark Hammond]
2. Remove depreciated pythoncom.MakeTime calls (now uses pywintypes.Time)
3. Change tests to default to local SQL server. 
4. Add an access-type database file for demo use.

Whats new in version 2.2.4
1. Ready for Python3? -- refactored so that 2to3 will inject very few errors, seems to be almost runnable in Pyk3.
2. Use new function getIndexedValue() to hide differences between IronPython and pywin32.

What happened to version 2.2.3?
   It was an attempt to be Python3 ready, but done wrong, so killed off.

whats new in version 2.2.2
1. Works with Iron Python 2.0RC1 (passes all tests except BINARY columns and old python time date conversion.)
2. Passes all dbapi20 tests (All errors and warnings are now defined for the connection object.)
3. Adds predefined conversion functions cvtBuffer and cvtUnicode if you want to use them.

Whats new in version 2.2.1
1. Bugfix for v2.1 item 6: but do not correct the string length if the output column is not a string.

Whats new in version 2.2
1. Runs on Iron Python 2.0b4 with a few restrictions. It will not handle Longs or BLOB correcly, 
   and has some date/time problems (using the "time" module as opposed to "datetime").
   Bug reports have been submitted to Iron Python, which, if fixed, will remove all restrictions.
2. More agressive at making sure to retrieve Numeric and Currency colums as decimal.Decimal.
3. Has a new conversion module. To make Numerics retrieve as strings, execute:
       adodbapi.variantConversions[adodbapi.adNumeric] = adodbapi.cvtString
4. Switch to new-style classes and eliminate string exceptions.
5. Lots of cleanup in the code and the unit test.
6. More agressive at determining .rowcount after an operation.

Whats new in version 2.1.1?
1. Bugfix so nextset() will work even if a rowset is empty [ Bob Kline ]
2. Bugfix to call CoInitailize() before calling Dispatch() [ Adam Vandenberg ]

Whats new in version 2.1?
1. Use of Decimal.decimal data type for currency and numeric data. [ Cole ]
2. add optional timeout parameter to the connect method i.e.: 
      adodbapi.connect(string,timeout=nuberOfSeconds)  [thanks to: Patrik Simons]
3. improved detection of underlying transaction support [ Thomas Albrecht ]
4. fixed record set closing bug and adoRowIDtype [ Erik Rose ]
5. client-side cursoring [ Erik Rose ]
6. correct string length for qmark parameter substitution [ Jevon a.k.a. Guybrush Threepwood ]
7. try-multiple-strategy loop replaced by other logic. [ Cole ]
8. correct error code raised when next recordset not available. [ ekelund ]
9. numerous changes in unit test (including test against mySQL)

Whats new in version 2.0.1?
Added missing __init__.py file so it installs correctly.

Whats new in version 2.0?
1. Improved performance through GetRows method.
2. Flexible date conversions. 
   Supports eGenix mxExtensions, python time module and python 2.3 datetime module.
3. More exact mappings of numeric datatypes. 
4. User defined conversions of datatypes through "plug-ins".
5. Improved testcases, not dependent on Northwind data.
6. Works with Microsoft Access currency datatype.
7. Improved DB-API 2.0 compliance.
8. rowcount property works on statements Not returning records.
9. "Optional" error handling extension, see DB-API 2.0 specification.

Installation
------------
For CPython, this version will be installed as part of the win32 package.
For IronPython (or to update a CPython version early), use "setup.py install"
while using the Python version upon which you want the package installed.

Authors (up to version 2.0.1)
-------
Henrik Ekelund, 
Jim Abrams.
Bjorn Pettersen.

Author (version 2.1 and later)
-------
Vernon Cole

License
-------
LGPL, see http://www.opensource.org/licenses/lgpl-license.php

Documentation
-------------
Start with:
http://www.python.org/topics/database/DatabaseAPI-2.0.html
read the examples in adodbapi/examples
and look at the test cases in adodbapi/test directory. 

Mailing lists
-------------
The adodbapi mailing lists have been deactivated. Submit comments to the 
pywin32 or IronPython mailing lists.
  -- the bug tracker on sourceforge.net/projects/adodbapi will be checked, (infrequently).
