#!/usr/bin/env python 

import sys, os, json, math, re, hashlib
from datetime import datetime, timedelta, time
import elasticsearch
from elasticsearch import Elasticsearch
import requests

#sys.path.append("/opt/utils")
#import filestoes, utils
#from utils import Map
from  mangorest.mango import webapi
import blogs.map

es         = Elasticsearch("http://localhost:9200")
INDEX_NAME = "suggest_index"

#--------------------------------------------------------------------------------
@webapi("/blogs/suggest")
def Suggest(q="", user="", prefs="", location="", **kwargs):
    r = es.search(index=INDEX_NAME, filter_path=[''], q=q, size=7)
    ret = [ f"{t['_source']['title']}" for t in r['hits']['hits'] ]
    ret = [k.replace("%20", " ") for k in list(set(ret))]

    if ( len(ret) < 10):
        response=Get3PSuggestions(q);
        for q in response.json()[1]:
            if ( len(ret) >= 10):
                break
            ret.append(q)

    ret = json.dumps(ret)
    
    print ("Suggest returning: ", ret[0:64])
    return ret
#-----------------------------------------------------------------------------------------------------------------
def InsertSuggestion( query="", user='unknonwn', es=es, **kwargs):
    query = query.strip() 
    if ( len(query) < 3 ):
        return 
    
    print(f'+++ indexing for {user}: {query}')
    id = hash(query)
    try:
        h = es.get(index=INDEX_NAME, id=id)
        print(f"Found an entry already for {query}")    
    except:
        h =None;
    
    if ( h is None):
        #userhash = hash(user)
        es.index(index=INDEX_NAME, id=id, 
                 body={
                    'title':query, 
                    'count': 0,
                    'id': id,      
                    'users': {},
                    'timeUTC': datetime.utcnow(), 
                    'timeLst': datetime.utcnow(), 
                })
        
        if ( len(query.split()) > 1 ): # Get suggestions from Google and insert it
            response=Get3PSuggestions(query);
            for q in response.json()[1]:
                print(f"==> Inserting Suggestions: {q}")
                id = hash(q)
                es.index(index= INDEX_NAME, id=id, body={
                    'title':q,  'count': 0,
                    'id': id,   
                    'users': {},
                    'timeUTC':  datetime.utcnow(), 
                    'timeLast': datetime.utcnow(), })
    else:
        u = h['_source']['users'].get(user,0) + 1
        body={
         "script": {
            "source" : f"ctx._source.count = ctx._source.count + 1; ctx._source.users['{user}'] = {u}",
             #"users" : {},
             "lang": "painless" },
          "query": { "terms": { "_id": [id] } },
            
        }
        h= es.update_by_query(index=INDEX_NAME,  body=body)
    return h;

#-------------------------------------------------------------------------------------------
# Search for some top 10 of last 10 searches for a users - 
# TODO: please review carefully
#
def seachSuggestedIndex(q="", IDS=[], users="".split('.'), es=es ):
    #lets make sure we got one entry in the system
    matchAll={'size': 30, "query": {"match_all": {}} }
    searchIDS = {"query": {"terms": { "_id": [IDS] }} }
                 
    # -> Search for all docs and print it
    if (len(IDS) > 0):
        ls = es.search(index=INDEX_NAME,body= searchIDS)
    elif( q is not None):
        ls = es.search(index=INDEX_NAME,q=q);
    else:
        print("Searching all ...")
        ls = es.search(index=INDEX_NAME,body= matchAll)
        
    for i,h in enumerate(ls['hits']['hits']):
        s = Map(h['_source'])
        ui= s.userid if s.userid else ""
        ta= ":".join ([str(k) for k in s.keys()])
        co= s.count if 'count' in s else "NA"
        print(f"{h['_id']:26} {i}/{ls['hits']['total']} count:{co:3} {ui:3} {s.utc} {s.title[0:10]} Tags: {ta}    ")
        
    return ls;

#-----------------------------------------------------------------------------------------------------------------
#Insert3PSuggestions(None, "Insight Rover", )
def Get3PSuggestions(query, proxies={'http':None, 'https': None}):
    #bq = urllib.parse.quote(query)
    #bs=f"http://api.bing.com/osjson.aspx?query={bq}"
    gq = re.subn('[ ]+','+',query)[0]
    gs=f"http://google.com/complete/search?q={gq}&output=chrome&hl=en"
    #print(f"{bs}\n{gs}")

    response=requests.get(gs,proxies=proxies, verify=False)    
    for c in response.json()[1]:
        print(c)
    return response

#-----------------------------------------------------------------------------------------------------------------
#es.indices.delete(index=INDEX_NAME)
def delFromSuggestedInex( es, title= 'stuff', id=None ):
    id = id if id else hash(title)
    timet = int(time.time())
    es.delete(index=INDEX_NAME, id=id)

#InsertSuggestion("First Some Test", user='sada')
