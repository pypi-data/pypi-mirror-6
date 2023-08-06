# -*- coding: UTF-8 -*-

"""
Get pollution info in Île-de-France from http://www.airparif.asso.fr/
"""

from bs4 import BeautifulSoup

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen  # Python 3

BASEURL = 'http://www.airparif.asso.fr/'

EU, FR = 'eu', 'fr'  # indices types


def get_indices(_type=EU):
    """
    Return a list of 3 integers representing indices for yesterday, today
    and tomorrow, using the given type (EU or FR).
    """
    doc = BeautifulSoup(urlopen(BASEURL))
    div = doc.select('#home_indices_%s' % _type)
    if not div:
        return None
    divs = div[0].select('.indices_data .selected')
    return map(lambda d: int(d.text), divs)


class PollutionFetcher():  # legacy class

    EU, FR = EU, FR

    def indices(self, _type=EU):
        "deprecated, use firapria.pollution.get_indices instead"
        return get_indices(_type)
