import os
import functools

import scarsdale_property_inquiry.download as dl

def get_dir():
    _dir = os.path.expanduser('~/dadawarehouse.thomaslevine.com/scarsdale-property-inquiry/info')
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    return _dir

def main():
    _dir = get_dir()
    session, street_ids = dl.home()
    street = functools.partial(dl.street, session)
    for street_id in street_ids:
        session, house_ids = street(street_id)
        house = functools.partial(dl.house, session)
        for house_id in house_ids:
            text = house(house_id)
            with open(os.path.join(_dir, house_id + '.html'), 'w') as fp:
                fp.write(text)
