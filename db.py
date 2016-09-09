#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sqlite3
print "douze"
conn = sqlite3.connect('data.db')
cursor =  conn.execute("select * from img")
print "cursor"
for row in cursor:
    print "id=", row[0]
    print "chemin", row[1]
    print "creation", row[2]
print "end"

    conn.execute('''DROP TABLE IMG''')
    conn.execute(''' CREATE TABLE IMG
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CHEMIN VARCHAR NOT NULL UNIQUE,
    CREATION DATE NOT NULL,
    MODIF DATE NOT NULL,
    KEYWORDS VARCHAR NOT NULL);''') 