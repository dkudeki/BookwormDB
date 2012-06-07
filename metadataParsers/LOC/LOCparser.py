#!/usr/bin/python

#Just running this to get the names:
#find LOCpapers/NewspaperFiles/ -name "*.txt" -exec basename {} \; > papers.txt

import re
import os
import json
import subprocess

filelist = open("../../../papers.txt")
metadata = open('../../../metadata/jsoncatalog.txt','w')
for line in filelist:
    mydict = dict()
    raw = line
    line = re.sub(".txt\n","",line)
    line = line.split("_")
    mydict['paperid'] = line[0]
    mydict['page'] = int(line[2])
    dates = line[1].split("-")
    mydict['year'] = int(dates[0])
    mydict['month'] = int(dates[1])
    mydict['day'] = int(dates[2])
    mydict['filename'] = re.sub(".txt\n","",raw)
    metadata.write(json.dumps(mydict)+"\n")
    if not os.path.exists("../../../texts/raw/"+re.sub("\n","",raw)):
        subprocess.call(['cp','../../../../LOCpapers/NewspaperFiles/'+re.sub("\n","",raw),"../../../texts/raw/"+re.sub("\n","",raw)])
