#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sqlite3
print "douze"
conn = sqlite3.connect('data2.db')
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
    CHEMIN_MINI VARCHAR NOT NULL UNIQUE,
    CREATION DATE NOT NULL,
    MODIF DATE NOT NULL,
    KEYWORDS VARCHAR NOT NULL);''')
conn.execute('''create table annotation
	(
	X1 INTEGER NOT NULL,
	Y1 INTEGER NOT NULL,
	X2 INTEGER NOT NULL,
	Y2 INTEGER NOT NULL,
	IMG integer not null,
	NB INTEGER NOT NULL,
	KEYWORDS VARCHAR NOT NULL,
	foreign key(IMG) references IMG(id),
	PRIMARY KEY (X1,Y1,X2,Y2,IMG) );''')
