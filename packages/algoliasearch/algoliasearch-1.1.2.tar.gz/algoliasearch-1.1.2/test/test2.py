from algoliasearch import algoliasearch
# -*- coding: utf-8 -*-
import pprint
import json
import time
import datetime

client = algoliasearch.Client("YXEKS4L3SV", '2b00207007e7564e0259181536f1cdef')
res = client.listIndexes()
print (res)
index = client.initIndex("bourrin")
res = index.setSettings({"customRanking": ["desc(followers)"]})
print (res)
#print client.copyIndex("contacts", "contacts2")
#print client.moveIndex("contacts2", "contacts3")
#print client.getLogs(0, 100)
