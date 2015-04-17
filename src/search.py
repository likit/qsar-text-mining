import os
import requests

api_key = os.environ['SCOPUS_APIKEY']
query = 'QSAR'
url = 'http://api.elsevier.com/content/search/scidir'
params = {'apiKey': api_key, 'query': query}

r = requests.get(url, params=params)
