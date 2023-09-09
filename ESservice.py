#!/usr/local/bin/python 

#*** DO NOT EDIT - GENERATED FROM ESsearch.ipynb ****

import logging as log
import sys, os, re, math, datetime, json, gc, urllib, elasticsearch, hashlib, pkgutil, requests, markdown
import pandas as pd
import numpy as np;
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers
from  mangorest.mango import webapi

#sys.path.append("/opt/utils")
#import filestoes
#from services.gen import suggestindex
#from services.gen import ESsearch
from blogs import suggestindex
from blogs import ESsearch

es = Elasticsearch("http://localhost:9200/")
#--------------------------------------------------------------------------------------------------------    
@webapi("/blogs/essearch")
def SearchES(q, user=None, params=None, DT1="1900", DT2="now/d", **kwargs):
    ret= ESsearch.SearchElastic(q, user, params, DT1=DT1, DT2=DT2);
    ret= ESsearch.Format(q, ret)
    
    try:
        if ( len(q) >= 3):
            suggestindex.InsertSuggestion(q, user or "unknown")
    except Exception as e:
        print("?: Suggested Index insertion Error! No worries")

    return ret
#--------------------------------------------------------------------------------------------------------    
@webapi("/essearchbyid")
def SearchESByID(ids, index='', **kwargs):
    cq = { "query": { "terms": {"_id": [f"{ids}"] }}}
          
    ls = es.search(index=index,  filter_path=[''], q=None, body=cq, size=5)
    ret = ls['hits']
    return ret;

#--------------------------------------------------------------------------------------------------------    
@webapi("/es_index_file")
def es_index_mdd(file, index='', **kwargs):
    op = filestoes.getfile(file, index)
    id = op['_source']['id']
    es.index(index=index, id=id, body=op['_source'])        
        
    return op;

#--------------------------------------------------------------------------------------------------------    
@webapi("/es_update")
def es_update(new_content, ids="", index='', **kwargs):
    body={
        "doc": {
            "content": new_content,
        }
     }
    es.update(index=index, body=body, id=ids)        
    return op;

#--------------------------------------------------------------------------------------------------------    
@webapi("/markdown")
def markit(text='', **kwargs):
    ret = markdown.markdown(text)
    #print(f'\n\n {text} ==> {ret} \n\n')
    
    return ret
#--------------------------------------------------------------------------------------------------------    
@webapi("/updatevote")
def incrementVote(id="__", score=.1, user="", index='', **kwargs):
    print( f"Ranking documents {id} to score {score} by User: {user}" )
    score = float(score)   #Score received must be b/w 0-5
    score = score - 2.5
    body={
        "script": {
            "source": "ctx._source.votes = Math.min(2.5, Math.max(0.1, ctx._source.votes + params.score))" ,
            "params": {
              "score": score
            },
            "lang": "painless"
        },
        "query": {"terms": { "_id": IDS }}
     }
    es.update_by_query(index=index, doc_type=doc_type, body=body)
    return ""
 
