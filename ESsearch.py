#!/usr/local/bin/python 

#*** DO NOT EDIT - GENERATED FROM ESsearch.ipynb ****

import logging as log
import sys, os, re, math, collections, gc, urllib, elasticsearch, hashlib, pkgutil, requests
import pandas as pd
import numpy as np;
import datetime, json
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

#sys.path.append("/opt/utils")
#import filestoes, utils
from blogs.map import Map

es = Elasticsearch("http://localhost:9200/")

EXCLUDE_INDICES =["suggest_index", "PRIVATE"]
def processQ(query, DT1="1900", DT2="now/d"):
    CQ=query
    AU=""
    TI=""
    FIELDS=[]
    
    sp = [re.subn('\s+', ' ', c.strip())[0] for c in query.split(',')]
    GEN=[]
    for c in sp:
        sp1 = c.split(':')
        if (len(sp1) <=1):
            GEN.append(sp1[0])
            continue;
        sp1[0] = sp1[0].lower().strip()
        if ( sp1[0] == "author"):
            AU=sp1[1].strip()
        elif ( sp1[0] == "title"):
            TI=sp1[1].strip()
        FIELDS.append(sp1[0])
    
    
    qBody = { #MAtch and boost
          "query": {
            "function_score": { 
                "query": {
                    "bool": {
                      "should": [
                        { "match": { 
                              "query": f"{CQ}",
                        }},
                        {"multi_match": {
                          "query":    f"{CQ}",
                          "fields": FIELDS
                        }},
                        { "match": { 
                            "attachment.content":  {
                              "query": f"{CQ}",
                              "boost": 1
                        }}},
                        { "match": { 
                            "attachment.author":  {
                              "query": f"{AU}",
                              "boost": 2
                        }}},
                        { "match": { 
                            "attachment.title":  {
                              "query": f"{TI}",
                              "boost": 2
                        }}},              ],
                        #"must": { "range" : { "attachment.date" : { "gte" : DT1, "lt" :  DT2}} }
                        },
                    }},
            #"field_value_factor": { "field": "votes"}
            }}
    print("returning ", qBody)
    return qBody;
    
def SearchElastic(query, user=None, params=None, index= "", typ ="", DT1="1900", DT2="now/d"):
    print(f"Searching {index} {typ} {query} {DT1} {DT2}")
    qBody = processQ(query, DT1=DT1, DT2=DT2)
    #ls = es.search(index=INDEX_NAME, _source_exclude=['data',], filter_path=[''], q=None, body=qBody, size=25)
    ls = es.search(index=index, filter_path=[''], q=None, body=qBody, size=25)
    print(qBody, f" Returned: {ls['hits']['total']}" )
    
    # Lets also index the query into the suggest index
    #suggestindex.InsertSuggest(es, query, user)
    
    ls = Map(ls)
    return ls;

def getContext(q,cont):
    op =""
    s = [c.lower() for c in q.split()];
    cont1 = cont.lower().strip();
    
    no = ""
    for w in s:
        idx = cont1.find(w)
        if ( idx < 0 ):
            if (len(no) <= 0):
                no = "Missing: <strike>"
                
            no +=  w + "</strike> &nbsp <strike>"
            continue;
            
        t = cont[max(0, idx-64):idx+64]
        op += t + "; ..."
        if ( len(op) > 1024 ): break;
        #print("GOT : ", w, "==>", op)

    no += "</strike>"
    
    for w in q.split():
        op = re.subn(w, f"<b><i><u>{w}</u></i></b>", op, flags=re.I|re.M)[0]
        
    return (op, no)

def getType(id):
    ret = ""
    if (not id): ret =""
    elif (id.endswith("pdf"))  : ret = "pdf"
    elif (id.endswith("doc"))  : ret = "doc"
    elif (id.endswith("docx")) : ret = "doc"
    elif (id.endswith("xls"))  : ret = "xls"
    elif (id.endswith("xlsx")) : ret = "xls"
    elif (id.endswith("ppt"))  : ret = "ppt"
    elif (id.endswith("pptx")) : ret = "ppt"
    
    return ret;
    
def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def Format(q, ls):
    ret = ""
    cnt = 0
    for i,h in enumerate(ls.hits['hits']):
        source = h['_index']
        if ( source in EXCLUDE_INDICES):
            continue
        cnt += 1
        s = Map(h['_source'])
        sc= h['_score']
        a = s
        if "attachment" in s:
            a = Map(s.attachment)
        c = a.content or  ''
        d = a.date
        t = f'{a.title}]' if a.title or a.title != None else f"Content: {c[0:48]}"
        au= a.author   if 'author'  in a else ''
        ed= a.editors  if 'editors' in a else ''
        ty= getType(h['_id'].lower())
        id = h['_id'];
        did  = f"r_{i}";
        vt = s['votes'] + 2.5 if 'votes' in s else 0
        vt = 5 if vt > 5 else vt
        vt = 0 if vt < 0 else vt
        rate = f'''<span style="display: inline-block;" id="{did}" ></span>
                <script> 
                    $("#{did}").rateYo({{rating: {vt}, id:"{id}", test:76, starWidth: "16px", onSet: rateInternalDoc }}); 
                </script>
                &nbsp;|&nbsp;
                '''
        
        tit,sumy,ctx,no = "", "", '', ''
        if (c.strip()):
            ctx,no = getContext(q, c)
            sumy= c[0: max(0, 512 - len(ctx))] + f" ... <b>Context: </b>{ctx}"
            sumy = cleanhtml(sumy)
            
        it = f'''
        <a onmouseover='viewDoc("{id}")' onclick='viewdetails("{id}", "{au}", "{ed}")' class='stitle {ty}' >
            {t}
        </a>
        <a onclick='edit("{id}", "{au}", "{ed}")'> &nbsp; <i class="fas fa-edit"></i> </a>
        
        [{i}]<p class='smeta'>{d} - <b>Rev: </b> {s.rev}, Author: <b>{au} </b> ID: {id} 
        <b>[Score: </b> {sc}]</p>
        <p class=abstract>{sumy}
        <a href=# onclick="thumbsup('{id}')"><i class="fas fa-thumbs-up"></i></a>&nbsp;
        <a href# onclick="thumbsdn('{id}')"><i class="fas fa-thumbs-down"></i></a>
         
         {rate}
        <br/>
        {no}
        </p><br/>
        '''
        ret += it;
    ret1= f'''Found {cnt} items in {ls.took} ms <br/><br/>'''
    
    ret = ret1 + ret
    return ret;

