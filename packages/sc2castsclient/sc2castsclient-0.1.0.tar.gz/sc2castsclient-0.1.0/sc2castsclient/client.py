#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from parser import Sc2CastsParser

# deals only with network requests; parsing is done elsewhere
class Sc2CastsClient:

    HOST = 'http://sc2casts.com'

    PATH_INDEX = '/index.php'
    PATH_TOP = '/top'
    PATH_BROWSE = '/browse'
    PATH_ALL = '/all'

    USER_AGENT = ''

    def log(self, message):
        print  message

    def __init__(self, user_agent=USER_AGENT):
        self.parser = Sc2CastsParser()
        self.user_agent = user_agent

    def series(self, filtertype='recent'):
        '''
        Query/filter for getting one or more casts, by 'type':

        { recent, top_24h, top_week, top_month, top_alltime, best_of_201[0123], all }
        '''
        if filtertype not in [ 'recent' ]:
            self.log('Unknown filtertype: ' + filtertype + '. Assuming recent')
            filtertype = 'recent'

        if filtertype == 'recent':
            url = self.HOST + self.PATH_INDEX
            html = requests.get(url).text
            return self.parser._parse_index(html)

    def series_by_path(self, path):
        url = self.HOST + path
        html = requests.get(url).text
        return self.parser._parse_series_page(html)
