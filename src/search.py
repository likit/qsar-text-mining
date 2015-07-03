import os
import requests
import xml.etree.ElementTree as et
import sys
import time
from datetime import datetime

api_key = os.environ['SCOPUS_APIKEY']

'''User defined variables.'''
query = 'qsar'
item_per_page = 25
start_year = 2010
end_year = 2016

url = 'http://api.elsevier.com/content/search/index:SCIDIR'
params = {'apiKey': api_key, 'query': query}
apikey = {'apiKey': api_key}

print >> sys.stderr, 'Downloading papers from year %d to %d' % (start_year, end_year)
print >> sys.stderr, 'Keyword(s) is "%s"' % (query)

r = requests.get(url, params=params)
total_results = int(r.json()['search-results']['opensearch:totalResults'])

page = 1
for start in range(0,total_results+1, item_per_page)
    print >> sys.stderr, 'Waiting to download from page %d...' % page
    time.sleep(5)
    page += 1
    url = 'http://api.elsevier.com/content/search/index:SCIDIR'
    params = {'apiKey': api_key,
                'query': query,
                'start': start,
                'count': item_per_page}

    articles = requests.get(url, params=params).json()['search-results']
    for n, entry in enumerate(articles['entry']):
        article_url = 'http://api.elsevier.com/content/article/%s' % (entry['dc:identifier'])
        article = requests.get(article_url, params=apikey)
        content = et.fromstring(article.text.encode('utf-8'))
        authors = []
        keywords = []
        for child in content.getchildren():
            for i in child:
                if 'creator' in i.tag:
                    authors.append(i.text.encode('utf8'))
                elif 'title' in i.tag:
                    title = i.text.encode('utf8')
                elif 'description' in i.tag:
                    desc = i.text.encode('utf8').lstrip('Abstract')
                elif 'publicationName' in i.tag:
                    pubname = i.text.encode('utf8')
                elif 'coverDate' in i.tag:
                    coverdate = i.text
                elif 'openaccessArticle' in i.tag:
                    openaccess_article = i.text
                elif 'subject' in i.tag:
                    keywords.append(i.text.encode('utf8'))

        coveryear = datetime.strptime(coverdate, '%Y-%m-%d').year
        if (coveryear >= start_year and coveryear < end_year):
            print '|'.join(authors) + '\t' + title + '\t' + desc + '\t' + ','.join(keywords) + '\t' + coverdate + '\t' + pubname + '\t' + openaccess_article
            print >> sys.stderr, n, title[:20]+'...', desc[:40]+'...', coverdate, '|'.join(authors)
