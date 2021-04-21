#!/usr/bin/python

import sqlite3 as sql
    
def createNewDatabase():
    conn = sqlite3.connect('database.db')
    print "Opened database successfully"
        
    conn.execute('CREATE TABLE students (name TEXT, addr TEXT, city TEXT, pin TEXT)')
    print "Table created successfully"
    conn.close()