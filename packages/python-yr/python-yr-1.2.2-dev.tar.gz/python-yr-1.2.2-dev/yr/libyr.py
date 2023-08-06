#!/usr/bin/env python3
import sys, json
from yr.utils import Location, Connect, Cache, Language

class Yr:

    def xmlsource(self):
        data = Connect(self.location).read()
        return data

    def xmltosoup(self, xml=None):
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            sys.stderr.write('import error: from bs4 import BeautifulSoup\n')
            sys.exit(1)
        if xml is None:
            return BeautifulSoup(self.xmlsource())
        else:
            return BeautifulSoup(xml)

    def xmltodict(self, xml=None):
        try:
            import xmltodict
        except ImportError:
            sys.stderr.write('import error: import xmltodict\n')
            sys.exit(1)
        if xml is None:
            return xmltodict.parse(self.xmlsource())
        else:
            return xmltodict.parse(xml)

    def xmltojson(self, xml=None):
        return json.dumps(self.xmltodict(xml), indent=4)

    def now(self, as_json=False): # default is return result as dict ;)
        soup = self.xmltosoup()
        xml = str(soup.forecast.tabular.time)
        if as_json:
            return self.xmltojson(xml)
        else:
            return self.xmltodict(xml)

    def __init__(self, location_name, language='en'):
        self.location_name = location_name
        self.language = language
        self._ = Language(self.language).get_dictionary()
        self.location = Location(self.location_name, self.language)
        self.yr_credit = {
            'text': self._['credit'],
            'url': 'http://www.yr.no/'
        }

    """
    def temperature(self):
        '''
        Get temperature from yr and return it.
        '''
        getlocation = Location(self.location_name, self.language).find()
        cache = Cache(getlocation, 'temperature')
        if cache.exists() and cache.is_fresh():
            return json.loads(cache.read())
        data = Connect(getlocation).read()
        data = et.fromstring(data)
        out = {}
        for parent in data[5].iter('temperature'):
            if parent.attrib:
                out['data'] = parent.attrib
        out['credit'] = self.yr_credit
        cache.write(json.dumps(out))
        return out

    def wind_speed(self):
        '''
        Get wind speed from yr.
        '''
        getlocation = Location(self.location_name, self.language).find()
        cache = Cache(getlocation, 'windspeed')
        if cache.exists() and cache.is_fresh():
            return json.loads(cache.read())
        data = Connect(getlocation).read()
        data = et.fromstring(data)
        out = {}
        for parent in data[5].iter('windSpeed'):
            if parent.attrib:
                out['data'] = parent.attrib
        out['credit'] = self.yr_credit
        cache.write(json.dumps(out))
        return out

    def wind_direction(self):
        '''
        Get wind direction from yr.
        '''
        getlocation = Location(self.location_name, self.language).find()
        cache = Cache(getlocation, 'wind_direction')
        if cache.exists() and cache.is_fresh():
            return json.loads(cache.read())
        data = Connect(getlocation).read()
        data = et.fromstring(data)
        out = {}
        for parent in data[5].iter('windDirection'):
            if parent.attrib:
                out['data'] = parent.attrib
        out['credit'] = self.yr_credit
        cache.write(json.dumps(out))
        return out

    def forecast(self):
        getlocation = Location(self.location_name, self.language).find()
        cache = Cache(getlocation, 'forecast')
        if cache.exists() and cache.is_fresh():
            return json.loads(cache.read())
        data = Connect(getlocation).read()
        data = et.fromstring(data)
        days = []
        for parent in data[5][0].iter('text'):
            for child in parent[0]:
                days.append({
                    'from': child.get('from'), 
                    'to': child.get('to'), 
                    child[0].tag: child[0].text, 
                    child[1].tag: child[1].text,
                })
        out = {}
        out['data'] = days
        out['credit'] = self.yr_credit
        cache.write(json.dumps(out))
        return out

    def observations(self):
        getlocation = Location(self.location_name, self.language).find()
        cache = Cache(getlocation, 'observations')
        if cache.exists() and cache.is_fresh():
            return json.loads(cache.read())
        data = Connect(getlocation).read()
        data = et.fromstring(data)
        observations = {}
        observations['data'] = {}
        for parent in data[6].iter('weatherstation'):
            stno = parent.attrib['stno']
            observations['data'][stno] = parent.attrib
            for child in parent:
                tag = child.tag
                observations['data'][stno][tag] = child.attrib
        observations['credit'] = self.yr_credit
        cache.write(json.dumps(observations))
        return observations

    def location_info(self):
        getlocation = Location(self.location_name, self.language).find()
        cache = Cache(getlocation, 'location')
        if cache.exists() and cache.is_fresh():
            return json.loads(cache.read())
        data = Connect(getlocation).read()
        data = et.fromstring(data)
        location_list = []
        location = {}
        for parent in data[0]:
            if parent.attrib:
                location_list.append(parent.attrib)
            else:
                location_list.append({
                    parent.tag: parent.text
                })
        location['data'] = location_list
        location['credit'] = self.yr_credit
        cache.write(json.dumps(location))
        return location
    """
