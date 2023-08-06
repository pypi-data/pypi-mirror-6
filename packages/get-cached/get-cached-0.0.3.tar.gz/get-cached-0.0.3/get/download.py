try:
    import requests
except ImportError:
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen
    def _get(url):
        fp = urlopen(url)
        if fp.code == 200:
            return fp.read()
        else:
            raise ValueError('Download failed')
else:
    def _get(url):
        r = requests.get(url)
        if r.ok:
            return r.content
        else:
            raise ValueError('Download failed')
