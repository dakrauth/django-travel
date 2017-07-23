import json
from itertools import chain
from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from travel import models as travel

FLAG_GROUPS = [
    ['AT', 'LV', 'PE', 'PF'],
    ['AX', 'FO', 'NO', 'IS'],
    ['XE', 'GE', 'XI', 'DK'],
    ['HR', 'SK', 'SI', 'RS'],
    ['RU', 'BG', 'LU', 'NL'],
    ['LT', 'BO', 'GH', 'ET'],
    ['XW', 'LK', 'BT', 'AL'],
    ['TD', 'RO', 'AD', 'MD'],
    ['GN', 'ML', 'SN', 'CM'],
    ['BF', 'MM', 'GH', 'GW'],
    ['ZW', 'UG', 'MU', 'CF'],
    ['JO', 'PS', 'SS', 'KW'],
    ['BE', 'DE', 'AM', 'TD'],
    ['VU', 'ZA', 'GY', 'ER'],
    ['CR', 'TH', 'CU', 'SR'],
    ['AU', 'NZ', 'TC', 'CK'],
    ['BH', 'QA', 'MT', 'NP'],
    ['AR', 'HN', 'SV', 'NI'],
    ['EG', 'YE', 'SY', 'IQ'],
    ['IR', 'TJ', 'HU', 'BG'],
    ['BW', 'GM', 'TZ', 'TT'],
    ['GR', 'UY', 'LR', 'MY'],
    ['CD', 'NA', 'KN', 'CG'],
    ['LA', 'NE', 'GL', 'BD'],
    ['NG', 'NF', 'LB', 'LS'],
    ['AZ', 'UZ', 'EH', 'KM'],
    ['PL', 'MC', 'ID', 'SG'],
    ['TN', 'TR', 'MA', 'MR'],
    ['DZ', 'MR', 'PK', 'TR'],
    ['FI', 'SE', 'DK', 'XE'],
    ['SC', 'MU', 'CF', 'KM'],
    ['DO', 'PA', 'MQ', 'BI'],
    ['AG', 'BB', 'BA', 'LC'],
    ['EC', 'CO', 'VE', 'AM'],
    ['HK', 'IM', 'KG', 'AL'],
    ['CI', 'IE', 'IT', 'IN'],
    ['BD', 'JP', 'PW', 'GL'],
    ['AS', 'MX', 'MD', 'ME'],
    ['AF', 'LY', 'KN', 'MW'],
    ['MH', 'NR', 'SB', 'CW'],
    ['BY', 'KZ', 'TM', 'IR'],
    ['CL', 'TO', 'TW', 'TG'],
    ['BJ', 'MG', 'OM', 'AE'],
    ['SL', 'UZ', 'RW', 'VC'],
    ['FM', 'AW', 'SO', 'TV'],
    ['GD', 'GP', 'DM', 'MV'],
    ['FJ', 'VG', 'AI', 'MS'],
    ['GQ', 'DJ', 'BS', 'PH'],
    ['AQ', 'CY', 'XK', 'MO'],
    ['LI', 'SM', 'VA', 'GI'],
    ['EE', 'GA', 'UA', 'SL'],
    ['IO', 'KI', 'CK'],
    ['AO', 'KE', 'SZ', 'ZM'],
    ['BZ', 'CV', 'SX', 'CZ'],
    ['FK', 'KY', 'BM', 'TV'],
    ['VN', 'CN', 'TW', 'KP'],
    ['SD', 'PS', 'JO', 'EH'],
    ['HT', 'LI', 'PT', 'MN'],
    ['PG', 'CX', 'CC', 'WS'],
    ['XS', 'XI', 'FI', 'XE'],
    ['JM', 'MK', 'ST', 'SC'],
    ['AO', 'MZ', 'SZ', 'KE'],
    ['BN', 'KH', 'TL', 'TK'],
    ['FR', 'IE', 'IT', 'CI'],
    ['GT', 'MX', 'PY', 'AR']
]

COUNTRY_CODES = list(chain(*FLAG_GROUPS))
FLAG_JSON = json.dumps(FLAG_GROUPS)

_flag_data = None

def get_flag_game_data():
    global _flag_data
    if _flag_data is None:
        countries = {
            co['code']: {
                "name": co['name'],
                "id": co['code'],
                "image": settings.MEDIA_URL + co['flag__svg']
            } for co in travel.TravelEntity.objects.countries().filter(
                code__in=COUNTRY_CODES
            ).select_related('flag').values('name', 'code', 'flag__svg')
        }
        _flag_data = {'countries': json.dumps(countries), 'groups': FLAG_JSON}
        
    return _flag_data


def flag_game(request):
    data = get_flag_game_data()
    return render(request, 'travel/flag-game.html', data)

