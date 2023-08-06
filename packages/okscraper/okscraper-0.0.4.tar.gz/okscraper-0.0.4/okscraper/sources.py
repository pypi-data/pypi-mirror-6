import re, urllib2

class BaseSource(object):
    """Abstract BaseSource
        extending classes must implement a fetch method which returns the data
    """

class BaseStringParamsSource(BaseSource):

    def __init__(self, source_string):
        self._source_string = source_string

    def fetch(self, *args, **kwargs):
        args = list(args)
        src = self._source_string
        identifiers = re.findall(r"<<(\w*)>>", src)
        while len(args) > 0 and len(identifiers) > 0:
            identifier = identifiers.pop(0)
            arg = args.pop(0)
            src = src.replace('<<{}>>'.format(identifier), str(arg))
        return self._fetch(src)

class UrlSource(BaseStringParamsSource):
    def _fetch(selfself, url):
        return urllib2.urlopen(url).read()

class FileSource(BaseStringParamsSource):
    def _fetch(self, filepath):
        with file(filepath) as f:
            return f.read()

class ScraperSource(BaseSource):

    def __init__(self, scraper):
        self._scraper = scraper

    def fetch(self, *args, **kwargs):
        return self._scraper.scrape(*args, **kwargs)
