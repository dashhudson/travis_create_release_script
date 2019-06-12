#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests
import json
import datetime
import re
import os


AUTH_TOKEN =os.environ['AUTH_TOKEN']

def get_last_release_tags(url):
    url=url+'tags'
    headers = {'Authorization': 'token ' + AUTH_TOKEN}

    res = requests.get(url, headers=headers)
    response = res.json()
    if len(response)>0:
        newest=response[0]['name']
        #newest='v0.1.23'
        m=re.findall('\d+',newest)
        if m:
            return [int(m[0]),int(m[1]),int(m[2])]
        raise Exception("Last release Tag not in proper format of vX.X.X")
    else:
        raise Exception("Didn't find any release tags, can't increment it")
    #print response


def tag_release(url,tag,name,message,object_SHA):
    url = url + 'releases'
    headers = {'Authorization': 'token ' + AUTH_TOKEN}
    payload = {
        'tag_name': tag,
        'name': name,
        'body': message,
        'target_commitish': object_SHA,
        'type': 'commit'
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 201:
        return response
    else:
        raise Exception("Can't tag release",response)

def increase_tag_number(tags):
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

def get_release_message(url,branch):
    url = url + 'commits/'+branch
    headers = {'Authorization': 'token ' + AUTH_TOKEN}

    res = requests.get(url, headers=headers)
    response = res.json()
    text=''
    if 'commit' in response:
        text=response['commit']['message']+'\n\n'
        text+=response['html_url']
    return text

if __name__ == "__main__":
    BASE_URL = 'https://api.github.com/repos/'
    PROJECT= os.environ['PROJECT_NAME']#'dashhudson/instagram-backend'
    BRANCH= os.environ['BRANCH_NAME'] #'master'

    tags = get_last_release_tags(BASE_URL + PROJECT + '/')
    tags = increase_tag_number(tags)
    tag='v{}.{}.{}'.format(tags[0],tags[1],tags[2])
    message= get_release_message(BASE_URL+PROJECT+'/',BRANCH)
    now = datetime.datetime.now()
    tag_release(BASE_URL+PROJECT+'/',tag,now.strftime("%B %d")+" Release",message,BRANCH)