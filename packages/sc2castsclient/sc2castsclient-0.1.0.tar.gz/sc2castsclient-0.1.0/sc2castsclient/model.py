#!/usr/bin/env python
# -*- coding: utf-8 -*-

# all paths are relative to HOST

class Sc2CastsHelpers(object):

    # really just 'non-breaking space'
    @staticmethod
    def unicode_cleanup(s):
        if s == None:
            return None
        return s.replace(u"\u00a0", " ")

class Sc2CastsCast(object):
    ''' A single video, embedded inside a series '''

    def __init__(self):
        self.name = None
        self.source = None
        self.video_url = None
        self.video_id = None
    def __repr__(self):
        return str(self.__dict__)

class Sc2CastsSeries(object):
    ''' Representation of a series: a single webpage with one or more videos, in total representing a cast of a series '''

    def __init__(self):
        self.name = None
        self.path = None
        #self.source = None

        # series meta
        self.matchup = None
        self.players = [ ]
        self.players_desc = None
        self.best_of = -1
        self.num_videos = 0
        self.event = None
        self.event_round = None
        self.casters = [ ]
        self.casters_desc = None
        self.cast_date = None

        self.score_up = -1
        self.score_down = -1

        # the actual casts themselves
        self.casts = [ ]

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, _name):
        self._name = Sc2CastsHelpers.unicode_cleanup(_name)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)

class Sc2CastsCaster(object):
    ''' '''

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
    def __str__(self):
        return self.name + ':' + self.path
    def __repr__(self):
        return str(self.__dict__)

class Sc2CastsEvent(object):
    ''' '''

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
    def __str__(self):
        return self.name + ':' + self.path
    def __repr__(self):
        return str(self.__dict__)

class Sc2CastsMatchup(object):
    ''' '''

    def __init__(self, name=None, path=None):
        # use setter
        self.name = name
        self.path = path
    @property
    def name(self):
        #print 'getter'
        return self._name
    @name.setter
    def name(self, _name):
        #print 'setter'
        if not _name == None:
            _name = _name.replace('[', '').replace(']', '')
        self._name = _name
    def __str__(self):
        return str(self.name) + ':' + str(self.path)

class Sc2CastsPlayer(object):
    ''' '''

    def __init__(self, name=None, path=None, sc2ranks_link=None):
        self.name = name
        self.path = path
        self.sc2ranks_link = sc2ranks_link
    def __str__(self):
        return str(self.name) + ':' + str(self.path) + ':' + str(self.sc2ranks_link)
    def __repr__(self):
        return str(self.__dict__)
