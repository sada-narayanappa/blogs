#!/usr/bin/env python 

#*** DO NOT EDIT - GENERATED FROM services.ipynb ****

from django.conf import settings
import os, json, sys, datetime, geoapp, logging
from  mangorest.mango import webapi
#import aiservices

BASE = "/opt/data/data/articles/raw/"
logger = logging.getLogger( "app.blogs")

#--------------------------------------------------------------------------------------------------------
FILES_DIRS = ("blogs/static/blogs/data/", "static/docs/", BASE)
UPLOADS_DIR = "blogs/static/blogs/uploads/"

def find(file, dirs=FILES_DIRS):
    if os.path.exists(file):
        return file
    for d in dirs:
        f = os.path.join(d, file)
        if os.path.exists(f):
            return f
    return None
#--------------------------------------------------------------------------------------------------------
@webapi("/blogs/getarticle")
def getarticle(request, file="", viewid="", dirs=FILES_DIRS, **kwargs):
    file = file or viewid
    f = find(file)
    if (not f):
        return f'{file} - does not exist!!!';

    cont = geoapp.utils.readfile(f )
    meta = json.loads(geoapp.utils.readfile(f+".meta", "{}"))
    title= meta.get('title', '')

    ret = { "title": title, "content": cont , "meta": meta, "dir": os.path.dirname(f) }
    return json.dumps(ret)
#--------------------------------------------------------------------------------------------------------    
@webapi("/blogs/savearticle")
def savearticle(request, user="noname", cfilename="", title="", contents="", **kwargs):
    if (not contents or not cfilename):
        return "No contents or cflename!!"

    file = find(cfilename)
    if (not file):
        #file = f"{user}-{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}.md"
        if (os.path.exists(FILES_DIRS[0])):   # First preference to blogs directory link if it exits
            file = FILES_DIRS[0] + cfilename
        else:
            file = FILES_DIRS[1] + cfilename

    logger.info(f"===> Saving {file} ...")
    indexed = file+".mdd"
    if os.path.exists(indexed):
        os.remove(indexed)

    meta = file+".meta"
    if os.path.exists(meta):
        os.remove(meta)

    dirn = os.path.dirname(cfilename)
    if(not os.path.exists(dirn) ): 
        os.makedirs( dirn ) 

    # Upload file attachments if any
    files = geoapp.utils.uploadFiles(request, UPLOADS_DIR )
    kwargs['files']    = files
    kwargs["filename"] = cfilename
    kwargs["title"]    = title
    kwargs["user"]     = user
    kwargs["date"]     = f"{datetime.datetime.utcnow()}" 

    with open(meta, "w") as f:
        f.write(json.dumps(kwargs, indent = 4) )

    with open(cfilename, "wb") as f:
        f.write(contents.encode('utf-8'))

    #os.system(f'/opt/utils/filestoes.py -d {FILES_DIRS[0]} -t "*.md" &')
        
    return f'Saved: {json.dumps(kwargs, indent = 4)} '
