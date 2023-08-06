import os

import requests
from randua import generate as ua
from randomsleep import randomsleep

import scarsdale_property_inquiry.params as p

def home(warehouse):
    if 'home' in warehouse:
        response = warehouse['home']
    else:
        randomsleep()
        response = requests.get(p.url(), headers = p.headers(ua()))
        warehouse['home'] = response
    return response

def _post(section_name, eventtarget):
    def f(warehouse, session, _id):
        key = (section_name, _id)
        if key in warehouse:
            response = warehouse[key]
        else:
            cookies, publickeytoken, viewstate, eventvalidation = session
            data = p.data(publickeytoken, viewstate, eventvalidation, eventtarget, _id)
            randomsleep()
            response = requests.post(p.url(), headers = p.headers(ua()), data = data, cookies = cookies)
            warehouse[key] = response
        return response
    return f

street = _post('street', 'dnn$ctr1381$ViewPIRPS$lstboxStreets')
house  = _post('house',  'dnn$ctr1381$ViewPIRPS$lstboxAddresses')
