# ***************************************************************************
# Copyright (c) 2013 SAP AG or an SAP affiliate company. All rights reserved.
# ***************************************************************************
#######################################################################
# 
# This sample program contains a hard-coded userid and password
# to connect to the demo database. This is done to simplify the
# sample program. The use of hard-coded passwords is strongly
# discouraged in production code.  A best practice for production
# code would be to prompt the user for the userid and password.
#
#######################################################################
import sqlanydb
import os, unittest
from runtests import test_sqlanydb

dbname = 'test'

def removedb(name):
    fname = name if name[-3:] == '.db' else name + '.db'
    if os.path.exists(fname):
	ret = os.system('dberase -y %s' % fname)
	if ret != 0:
	    raise Exception('dberase failed (%d)' % ret)

def cleandb(name):
    removedb(name)
    ret = os.system('dbinit %s' % name)
    if ret != 0:
	raise Exception('dbinit failed (%d)' % ret)

if __name__ == '__main__':
    cleandb(dbname)
    # Auto-start engine
    c = sqlanydb.connect(uid='dba', pwd='sql', dbf=dbname)
    results = open('summary.out', 'w+')
    unittest.main(testRunner=unittest.TextTestRunner(results))
    results.close()
    c.close()
    removedb(dbname)
