import os

import requests
from randua import generate as ua
from pickle_warehouse import Warehouse

import scarsdale_property_inquiry.params as p

_dir = os.path.expanduser('~/dadawarehouse.thomaslevine.com/scarsdale-property-inquiry/requests')
_warehouse = Warehouse(_dir)

def home():
    if 'home' in _warehouse:
        response = _warehouse['home']
    else:
        response = requests.get(p.url(), headers = p.headers(ua()))
        _warehouse['home'] = response
    return response

def _post(section_name, eventtarget):
    def f(session, _id):
        key = (section_name, _id)
        if key in _warehouse:
            response = _warehouse[key]
        else:
            cookies, publickeytoken, viewstate, eventvalidation = session
            data = p.data(publickeytoken, viewstate, eventvalidation, eventtarget, _id)
            response = requests.post(p.url(), headers = p.headers(ua()), data = data, cookies = cookies)
            _warehouse[key] = response
        return response
    return f

street = _post('street', 'dnn$ctr1381$ViewPIRPS$lstboxStreets')
house  = _post('house',  'dnn$ctr1381$ViewPIRPS$lstboxAddresses')
