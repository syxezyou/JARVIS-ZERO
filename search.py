import os, requests, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

SESSION = requests.Session()
SESSION.headers.update({'User-Agent':'JARVIS-Research/0.1 (+personal research assistant)'})

def search_web(question):
    base = os.getenv('SEARXNG_URL', 'https://searx.be').rstrip('/')
    if not base.startswith('https://') and not base.startswith('http://'):
        raise ValueError('Invalid SearXNG URL')
    r = SESSION.get(base + '/search', params={'q': question, 'format': 'json', 'language':'fr-FR'}, timeout=12)
    r.raise_for_status()
    data = r.json()
    results=[]
    for item in data.get('results', []):
        url=item.get('url','')
        parsed=urlparse(url)
        if parsed.scheme != 'https' or not parsed.hostname:
            continue
        title=re.sub(r'\s+', ' ', BeautifulSoup(item.get('title',''), 'html.parser').get_text(' ', strip=True))[:180]
        snippet=BeautifulSoup(item.get('content',''), 'html.parser').get_text(' ', strip=True)[:650]
        if title and snippet:
            results.append({'title':title, 'url':url, 'snippet':snippet})
        if len(results)==8: break
    return results
