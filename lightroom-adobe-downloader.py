#!/usr/bin/env python3

import requests
import json
import mimetypes
import os.path
import sys
from fake_useragent import UserAgent
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

arg = sys.argv[1:]
if len(arg) != 1:
    print("Give only ID of the share as parameter")
    exit(1)

session = requests.Session()
session.headers['User-Agent'] = UserAgent(os='windows').random

share=arg[0]
downloadfolder='assets'
statusfolder='status'

if not os.path.exists(downloadfolder):
    os.makedirs(downloadfolder)
if not os.path.exists(statusfolder):
    os.makedirs(statusfolder)

count=0
r = session.get('https://lightroom.adobe.com/shares/' + share)
if r.status_code == 404:
    print("ID not found")
    exit()
html = r.text
soup = BeautifulSoup(html, "html.parser")
scripts = soup.select('script')
for i in scripts:
    tmp1 = i.text
    tmp2 = tmp1.split("\n")
    for j in tmp2:
        if "spaceAttributes:" in j:
            tmp3 = j

tmp4 = json.loads(tmp3.split(':', 1)[1][:-1])
for i in tmp4['resources']:
    if i['type'] == "album":
        album = i['id']
        print("Process Album: " + album)
        
        for mediatype in ['image', 'video']:
            print("Download: " + mediatype)
            tmp1 = session.get('https://lightroom.adobe.com/v2/spaces/' + share + '/albums/' + album + '/assets?embed=asset;user&subtype=' + mediatype + ';layout_segment').text
            tmp2 = "\n".join(tmp1.split("\n")[1:])
            tmp3 = json.loads(tmp2)
            # print(tmp3)
            last = False
            while last == False:
                for i in tmp3['resources']:
                    if i['type'] == "album_asset":
                        assets = i['asset']['id']
                        count += 1
                        statusname = album + '-' + assets + '-' + i['asset']['subtype']
                        if os.path.isfile(statusfolder + '/' + statusname):
                            if False:
                                print("Already found! " + statusname)
                        else:
                            name = ".".join(i['asset']['payload']['importSource']['fileName'].split('.')[:-1])
                            # print(json.dumps(i, indent=4))
                            print("Process Asset: " + assets)
                            print('URL: https://dl.lightroom.adobe.com/spaces/' + share + '/assets/' + assets)
                            r = session.get('https://dl.lightroom.adobe.com/spaces/' + share + '/assets/' + assets)
                            filename = statusname + '-' + name + mimetypes.guess_extension(r.headers['content-type'])
                            print("Save to: " + filename)
                            with open(downloadfolder + '/' + filename, 'wb') as f:
                                f.write(r.content)
                            open(statusfolder + '/' + statusname, 'a').close()
                    else:
                        print(i['type'])
                if 'links' in tmp3 and 'next' in tmp3['links']:
                    tmp1 = session.get('https://lightroom.adobe.com/v2/spaces/' + share + '/' + tmp3['links']['next']['href']).text
                    tmp2 = "\n".join(tmp1.split("\n")[1:])
                    tmp3 = json.loads(tmp2)
                else:
                    last = True
        # print(json.dumps(tmp3, indent=2))

            
print("Found and downloaded assets: " + str(count))
