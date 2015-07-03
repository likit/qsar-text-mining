import os
import requests
import xml.etree.ElementTree as et

api_key = os.environ['SCOPUS_APIKEY']
query = 'qsar'
url = 'http://api.elsevier.com/content/search/index:SCIDIR'
params = {'apiKey': api_key, 'query': query}
key_param = {'apiKey': api_key}

r = requests.get(url, params=params)
total_results = int(r.json()['search-results']['opensearch:totalResults'])
item_per_page = int(r.json()['search-results']['opensearch:itemsPerPage'])

print total_results
print item_per_page

for start in range(0,total_results+1, 25)[:1]:
    url = 'http://api.elsevier.com/content/search/index:SCIDIR'
    params = {'apiKey': api_key,
                'query': query,
                'start': start,
                'count': item_per_page}

    articles = requests.get(url, params=params).json()['search-results']
    for entry in articles['entry']:
        article_url = 'http://api.elsevier.com/content/article/%s' % (entry['dc:identifier'])
        article = requests.get(article_url, params=params)
        content = et.fromstring(article.text.encode('utf-8'))
        authors = []
        for child in content.getchildren():
            for i in child:
                if 'creator' in i.tag:
                    authors.append(i.text)
                if 'description' in i.tag:
                    desc = i.text
        print ','.join(authors) + '\t' + desc
