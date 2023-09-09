import json

from django.shortcuts import render
from django.http import HttpResponse
from mangorest import mango
import sys, os, shutil, datetime, re

'''
import aiapp.utils

sys.path.append("/opt/utils/")
import services.gen.FileServices as FileServices

APPNAME   ='blogs'

def blogedit(request):
    parms = mango.getparms(request)
    id = parms.get('id', None)
    if ( not id):
        return render(request, 'index.html')

    # get the document from es
    # check for permissions
    # if not authorized send them to error page
    # else: take them to edit page.

    return render(request, 'index.html')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BASE = f"/opt/data/data/articles/"

def uploadFiles(request):
    parms = mango.getparms(request)
    user = parms.get("user", "noname")
    del parms['csrfmiddlewaretoken']
    del parms['request']
    print(f"Uploading Files from {user} {parms}")
    ret = FileServices.uploadFile(request, "imgs.txt", savein=f"{BASE}/imgs", **parms);
    return HttpResponse(ret)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getarticles(request):
    parms = mango.getparms(request)
    user = parms.get("user", "noname")

    filelist = f"{BASE}{user}.articles.csv"
    #print(f"^ Getting article list for {user} from: {filelist}")

    if ( not os.path.exists(filelist)):
        filelist = f"{BASE}default.articles.csv"
        #shutil.copy(filelist, deffilelist)

    df, ret = aiapp.utils.read_csv(filelist)

    return HttpResponse(json.dumps(ret));
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#@ This will save the name and title of the files in users articles file
#@ this will be used to retrieve all the articles written by the user
#@
def saveArticles(user, name, title):
    user = user or "noname"
    file = f"{BASE}{user}.articles.csv"
    cont = aiapp.utils.readfile(file,"name, title\n\n").strip()

    line = f"\n{name}, '{title}'"
    print(f"?==> Checking for ENTRY {line}")

    if ( cont.find(line) >=0 ):
        print(f"+ Found {line}; No Need to add!!")
        return cont;
    if ( cont.find(name) >=0 ):
        print(f"+ Found {name} different title!!")
        cont = re.sub(f'\n{name},.*\n', f"\n{line}\n", cont);
    else:
        cont += line

    print(f"Saving the list to {file}")
    cont = aiapp.utils.writefile(file, cont)

    return cont
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getarticle(request):
    parms = mango.getparms(request)
    user = parms.get("user", "noname")
    file = parms.get("file", "default.md")

    ffile = f"{BASE}raw/{file}"
    if ( not ffile.endswith("md")):
        ffile += ".md"

    if ( not os.path.exists(ffile)):
        print( f'- Tried {ffile}')
        return HttpResponse(f'{file} - does not exist!!!');

    cont = aiapp.utils.readfile(ffile)
    meta = json.loads(aiapp.utils.readfile(ffile+".meta", "{}"))
    title= meta.get('title', '')

    ret = { "title" : title, "content": cont , "meta": meta }
    return HttpResponse(json.dumps(ret) );
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def putarticle(request):
    parms = mango.getparms(request)
    user  = parms.get("user", "noname")
    cfile = parms.get("cfilename", "")
    title = parms.get("title", "No title")

    if (not cfile):
        datet = ""
        cfile = f"{user}-{datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.md"
        parms["cfilename"] = cfile
        print("Creating a new file {cfile}")

    del parms['request']
    ret = FileServices.uploadFile(request=request, savein=f'{BASE}raw', **parms);
    saveArticles(user,cfile, title)
    indexed = f"{BASE}raw/{cfile}.mdd"
    if os.path.exists(indexed):
        os.remove(indexed)

    print ("RUNNING Indexing command")
    os.system('/opt/utils/filestoes.py -d "/opt/data/data/articles/raw" -t "*.md" &')
    return HttpResponse( cfile + "\n" + ret )
'''
