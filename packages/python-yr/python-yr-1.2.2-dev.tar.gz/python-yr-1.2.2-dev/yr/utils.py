#!/usr/bin/env python3
import os.path, sys, json, hashlib, requests, tempfile, datetime

class Language:

    def __init__(self, language):
        self.language = language

    def get_dictionary(self):
        path = os.path.abspath(os.path.dirname(__file__))
        filename = '{}/languages/{}.json'.format(path, self.language)
        if os.path.exists(filename):
            if sys.version_info[:2] == (2, 7):
                import codecs
                with codecs.open(filename, mode='r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(filename, mode='r', encoding='utf-8') as f:
                    return json.load(f)
        else:
            sys.stderr.write('error: unsupported language ~> {}\n'.format(self.language))
            sys.exit(1)

class Location:

    def __init__(self, location_name, language):
        self.location_name = location_name
        self.language = language
        self._ = Language(self.language).get_dictionary()
        self.url = self.get_url()
        self.hash = self.get_hash()

    def get_url(self):
        result = 'http://www.yr.no/{place}/{location_name}/{forecast}.xml'.format(location_name=self.location_name, **self._)
        return result

    def get_hash(self):
        result = hashlib.sha256(self.location_name.encode('utf-8')).hexdigest()[:12]
        return result

class Connect:

    def __init__(self, location):
        self.location = location

    def read(self):
        cache = Cache(self.location, 'forecast')
        if not cache.exists() or not cache.is_fresh():
            yr = requests.get(self.location.url)
            if not yr.status_code == requests.codes.ok:
                yr.raise_for_status()
            cache.write(yr.text) #.encode('utf-8') $$bug$$ ~> create empty forecast file in my /tmp/
        data = cache.read()
        return data

class Cache:

    cache_timeout = 30 # cache timeout in minutes

    def __init__(self, location, what):
        self.location = location
        self.cache_filename = '{}/{}.{}'.format(tempfile.gettempdir(), self.location.hash, what)

    def write(self, data):
        if sys.version_info[:2] == (2, 7):
            import codecs
            with codecs.open(self.cache_filename, mode='w', encoding='utf-8') as f:
                f.write(data)
        else:
            with open(self.cache_filename, mode='w', encoding='utf-8') as f:
                f.write(data)

    def is_fresh(self):
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.cache_filename))
        result = datetime.datetime.now() - modified <= datetime.timedelta(minutes=self.cache_timeout)
        return result

    def exists(self):
        result = os.path.isfile(self.cache_filename)
        return result

    def read(self):
        if sys.version_info[:2] == (2, 7):
            import codecs
            with codecs.open(self.cache_filename, mode='r', encoding='utf-8') as f:
                data = f.read()
                return data
        else:
            with open(self.cache_filename, mode='r', encoding='utf-8') as f:
                data = f.read()
                return data
