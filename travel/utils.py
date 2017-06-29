# -*- coding:utf8 -*-
import io
import re
import json
import datetime
from urllib.parse import quote_plus, unquote

from decimal import Decimal, localcontext
import requests
from PIL import Image
from dateutil.parser import parser, parserinfo
from unidecode import unidecode


def normalize_file_from_url(u):
    fn = u.rsplit('/', 1)
    fn = fn[1] if len(fn) == 2 else fn[0]
    return unidecode(unquote(fn)).lower()


class DateParserInfo(parserinfo):
    parserinfo.MONTHS[8] += ('Sept',)
    parserinfo.WEEKDAYS[1] += ('Tues',)
    parserinfo.WEEKDAYS[2] += ('Weds', 'Wedn')
    parserinfo.WEEKDAYS[3] += ('Thurs', 'Thur')


dt_parser = parser(DateParserInfo()).parse


def nice_url(text):
    return quote_plus(text)


def get_url_content(url):
    r = requests.get(url)
    return r.content if r.ok else None


class LatLonParser:

    latlon_sym_re = re.compile(
        r'''
            ([+-]?\d+)[º°]?\s*
            (?:(\d+)['′])?\s*
            (?:(\d+)["″])?\s*
            ([NS])?
            \s*[,/]?\s*
            ([+-]?\d+)[º°]?\s*
            (?:(\d+)['′])?\s*
            (?:(\d+)["″])?\s*
            ([EW])?
        ''',
        re.VERBOSE
    )

    latlon_dec_re = re.compile(
        r'''^
            ([+-]?\d+\.\d+)\s*
            ([NS])?
            \s*[,/]?\s*
            ([+-]?\d+\.\d+)\s*
            ([EW])?
        $''',
        re.VERBOSE
    )

    def make_decimal(self, degs='0', mins=None, secs=None, negative=False):
        with localcontext() as ctx:
            ctx.prec = 6
            degs = Decimal(degs)
            mins = Decimal(mins or '0')
            secs = Decimal(secs or '0')
            degs += (mins / Decimal('60')) + (secs / Decimal('3600'))
            return -degs if negative else degs

    def parse(self, s):
        m = self.latlon_dec_re.search(s)
        if m:
            lat_d, lat_dir, lon_d, lon_dir = m.groups()
            lat_m = lat_s = lon_m = lon_s = None
        else:
            m = self.latlon_sym_re.search(s.strip())
            if m:
                lat_d, lat_m, lat_s, lat_dir, lon_d, lon_m, lon_s, lon_dir = m.groups()

        if m:
            lat_dir = lat_dir or 'N'
            lon_dir = lon_dir or 'E'
            lat = self.make_decimal(lat_d, lat_m, lat_s, lat_dir.lower() == 's')
            lon = self.make_decimal(lon_d, lon_m, lon_s, lon_dir.lower() == 'w')
            
            return [lat, lon]
        
        raise ValueError('Invalid Lat/Lon value: %s' % (s,))

parse_latlon = LatLonParser().parse

class TravelJsonEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    
    DATE_FORMAT     = "%Y-%m-%d"
    TIME_FORMAT     = "%H:%M:%S"
    DATETIME_FORMAT = '{}T{}Z'.format(DATE_FORMAT, TIME_FORMAT)
    

    def _special(self, ctype, value):
        return {'content_type': ctype, 'value': value}
        

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return self._special('datetime', o.strftime(self.DATETIME_FORMAT))
        elif isinstance(o, datetime.date):
            return self._special('date', o.strftime(self.DATE_FORMAT))
        elif isinstance(o, datetime.time):
            return self._special('time', o.strftime(self.TIME_FORMAT))
        elif isinstance(o, Decimal):
            return self._special('decimal', str(o))
        
        return super(TravelJsonEncoder, self).default(o)


DATETIME_PARSERS = dict(
    datetime = lambda o: datetime.datetime.strptime(o, TravelJsonEncoder.DATETIME_FORMAT),
    date     = lambda o: datetime.date(*[int(i) for i in o.split('-')]),
    time     = lambda o: datetime.time(*[int(i) for i in o.split(':')]),
    decimal  = Decimal
)


def object_hook(dct):
    content_type = dct.get('content_type')
    if content_type in DATETIME_PARSERS:
        return DATETIME_PARSERS[content_type](dct['value'])

    return dct


def json_dumps(obj, cls=TravelJsonEncoder, **kws):
    return json.dumps(obj, indent=kws.pop('indent', 4), cls=cls, **kws)


def json_loads(s, object_hook=object_hook, **kws):
    return json.loads(s, object_hook=object_hook, **kws)

