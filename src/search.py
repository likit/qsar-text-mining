# coding:utf-8
import os
import requests
import xml.etree.ElementTree as et
import json
import sys
import time
import pymongo
import re
from datetime import datetime

db = pymongo.Connection()['data']

api_key = os.environ['SCOPUS_APIKEY']

'''User defined variables.'''
item_per_page = 200
pub_year = 2015
outfile_prefix = 'qsar'
query = 'tak(qsar) AND pub-date IS %d' % pub_year
sleeptime = 5

url = 'http://api.elsevier.com/content/search/index:SCIDIR'
params = {'apiKey': api_key, 'query': query}
apikey = {'apiKey': api_key}

print >> sys.stderr, 'Downloading papers published in %d' % pub_year
print >> sys.stderr, 'Query is "%s"' % (query)

r = requests.get(url, params=params)
total_results = int(r.json()['search-results']['opensearch:totalResults'])
print >> sys.stderr, 'Total articles = %d' % total_results

page = 0
for start in range(0,total_results+1, item_per_page):
    print >> sys.stderr, 'Waiting %d sec to download from page %d...' % \
                                (sleeptime, page+1)
    time.sleep(sleeptime)
    # op = open('%s_page_%d_%d' % (outfile_prefix, page+1, pub_year), 'w')
    url = 'http://api.elsevier.com/content/search/index:SCIDIR'
    params = {'apiKey': api_key,
                'query': query,
                'start': start,
                'count': item_per_page}

    articles = requests.get(url, params=params).json()['search-results']
    for n, entry in enumerate(articles['entry']):
        print >> sys.stderr, '\tdownloading %s...' % entry['dc:title'][:25]
        article_url = 'http://api.elsevier.com/content/article/%s' % (entry['dc:identifier'])
        article = requests.get(article_url, params=apikey)
        content = et.fromstring(article.text.encode('utf-8'))
        article_dict= {}
        for child in content.getchildren():
            for i in child:
                tag = re.match('(\{([^}]+)\})(.*)',
                        i.tag.encode('utf-8')).groups()[-1]
                if tag not in article_dict:
                    if i.text:
                        article_dict[tag] = [i.text.encode('utf-8')]
                    else:
                        article_dict[tag] = [None]
                else:
                    if i.text:
                        article_dict[tag].append(i.text.encode('utf-8'))
                    else:
                        article_dict[tag].append(None)

        existing_article = db.scopus.find_one({'identifier': article_dict['identifier']})
        if not existing_article:
            db.scopus.insert(article_dict, safe=True)
        else:
            print >> sys.stderr, 'The article already exists.'
    page += 1
