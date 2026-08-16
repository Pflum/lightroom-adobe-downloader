#!/usr/bin/env python3

import requests
import json
import mimetypes
import os.path
import sys
import logging
from fake_useragent import UserAgent
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logging.info('Adobe Lightroom Downloader')

arg = sys.argv[1:]
if len(arg) != 1:
    logging.critical("Give only ID of the share as parameter")
    exit(1)

session = requests.Session()
session.headers['User-Agent'] = UserAgent(os='Windows').random

share=arg[0]
downloadfolder='assets'
statusfolder='status'

if not os.path.exists(downloadfolder):
    os.makedirs(downloadfolder)
if not os.path.exists(statusfolder):
    os.makedirs(statusfolder)

foundcount=0
downloadcount=0
skippedcount=0
failedcount=0
r = session.get('https://lightroom.adobe.com/shares/' + share)
if r.status_code == 404:
    logging.critical("ID not found")
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
        logging.debug("Process Album: " + album)
        
        for mediatype in ['image', 'video']:
            logging.debug("Download: " + mediatype)
            tmp1 = session.get('https://lightroom.adobe.com/v2/spaces/' + share + '/albums/' + album + '/assets?embed=asset;user&subtype=' + mediatype + ';layout_segment').text
            tmp2 = "\n".join(tmp1.split("\n")[1:])
            tmp3 = json.loads(tmp2)
            last = False
            while last == False:
                for i in tmp3['resources']:
                    if i['type'] == "album_asset":
                        assets = i['asset']['id']
                        foundcount += 1
                        statusname = album + '-' + assets + '-' + i['asset']['subtype']
                        if os.path.isfile(statusfolder + '/' + statusname):
                            logging.debug("Already found! " + statusname)
                            skippedcount += 1
                        else:
                            name = ".".join(i['asset']['payload']['importSource']['fileName'].split('.')[:-1])
                            logging.info("Process Asset: " + assets)
                            logging.debug('URL: https://dl.lightroom.adobe.com/spaces/' + share + '/assets/' + assets)
                            r = session.get('https://dl.lightroom.adobe.com/spaces/' + share + '/assets/' + assets)
                            extension = mimetypes.guess_extension(r.headers['content-type'])
                            if extension is not None:
                                filename = statusname + '-' + name + extension
                                logging.debug("Save to: " + filename)
                                with open(downloadfolder + '/' + filename, 'wb') as f:
                                    f.write(r.content)
                                open(statusfolder + '/' + statusname, 'a').close()
                                downloadcount += 1
                            else:
                                logging.warning("Download failed, returned: " + str(r.content))
                                failedcount += 1
                    else:
                        logging.critical("Unkown resource: " + i['type'])
                if 'links' in tmp3 and 'next' in tmp3['links']:
                    tmp1 = session.get('https://lightroom.adobe.com/v2/spaces/' + share + '/' + tmp3['links']['next']['href']).text
                    tmp2 = "\n".join(tmp1.split("\n")[1:])
                    tmp3 = json.loads(tmp2)
                else:
                    last = True
            
logging.info(str(foundcount) + " assets found")
logging.info(str(skippedcount) + " assets skipped (already downloaded)")
logging.info(str(downloadcount) + " assets downloaded")
logging.info(str(failedcount) + " assets failed!")
