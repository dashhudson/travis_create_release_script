#!/usr/bin/python

import re
from sys import argv

def increase_version_number(tags):
    if tags[2]<10:
        tags[2]+=1
    else:
        tags[2]=0
        if tags[1]<10:
            tags[1]+=1
        else:
            tags[1]=0
            tags[0]+=1
    return tags

def check_semver(version):
    m =  re.findall('\d+',version)
    if m:
        return [int(m[0]),int(m[1]),int(m[2])]
    raise Exception("Last release Tag not in proper format of vX.X.X")

current_version = check_semver(argv[1])
new_version = increase_version_number(current_version)

res = str(".".join(map(str, new_version)))

print("v" + res)
