# -*- coding: UTF-8 -*-

"""
Get pollution info in Île-de-France from http://www.airparif.asso.fr/
"""

from bs4 import BeautifulSoup
from urllib import urlopen


class PollutionFetcher():

    EU, FR = 'eu', 'fr'  # indices types

    def __init__(self):
        self.doc = None
        self.fetch_from = 'http://www.airparif.asso.fr/'

    def __fetch(self):
        self.doc = BeautifulSoup(urlopen(self.fetch_from))

    def indices(self, _type=EU):
        """
        Return a list of 3 integers representing indices for yesterday, today
        and tomorrow, using the given type (EU or FR).
        """
        if self.doc is None:
            self.__fetch()
        div = self.doc.select('#home_indices_%s' % _type)
        if not div:
            return None
        divs = div[0].select('.indices_data .selected')
        return map(lambda d: int(d.text), divs)
