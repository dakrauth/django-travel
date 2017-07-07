import datetime
from decimal import Decimal

import pytest

from travel import utils

class TestJSONEncoding:

    def test_json_encoding(self):
        data = dict(
            a_date=datetime.date(2011, 4, 22),
            a_time=datetime.time(16, 59, 59),
            a_datetime=datetime.datetime(2009, 2, 9, 8, 15),
            a_decimal=Decimal('19.65'),
            an_int=77
        )
        out = utils.json_dumps(data)
        print(out)
        result = utils.json_loads(out)
        assert data == result

    
class TestLatLonParsing:

    def test_lat_lon(self):
        expect = [Decimal('12.34'), Decimal('56.78')]
        threshold = Decimal('0.1')
        for i, item in enumerate([
            '12.34 56.78',
            '12.34, 56.78',
            '12.34N 56.78 E',
            '12.34 N, 56.78 E',

            '12°20′24″ 56°46′48″',
            '12°20′24″, 56°46′48″',
            '12°20′24″N 56°46′48″E',
            '12°20′24″N, 56°46′48″E',

            '12º20′24″ 56º46′48″',
            '12º20′24″, 56º46′48″',
            '12º20′24″N 56º46′48″E',
            '12º20′24″N, 56º46′48″E',
        ]):
            print(i)
            lat, lon = utils.parse_latlon(item)
            print(lat, lon)
            delta = abs(lat - expect[0])
            print(delta)
            assert  delta < threshold
            
            delta = abs(lon - expect[1])
            print(delta)
            assert delta < threshold

    def test_bad_latlon(self):
        with pytest.raises(ValueError):
            utils.parse_latlon('124')
            utils.parse_latlon('124W 15E')
            utils.parse_latlon("1°60' 15E")
            utils.parse_latlon('90.5, 123')
            utils.parse_latlon('89.5, 180.1')


class TestNiceFormats:

    def test_nice_filename(self):
        assert utils.normalize_file_from_url('/a/b/Le%C3%B3n.txt') == 'leon.txt'
        assert utils.normalize_file_from_url(
            'http://example.org/commons/Pyr%C3%A9n%C3%A9es.svg'
        ) == 'pyrenees.svg'
