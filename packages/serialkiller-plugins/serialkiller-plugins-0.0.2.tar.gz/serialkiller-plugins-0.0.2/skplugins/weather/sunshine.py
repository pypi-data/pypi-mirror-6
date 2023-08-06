#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ephem

from skplugins import skplugins


class sunshine(skplugins):
    """Check if day or night"""
    def __init__(self, **kwargs):
        super(sunshine, self).__init__(**kwargs)
        self._types = {
            'result': 'byte',
        }
        self.check()

    @property
    def params(self):
        """Get Value"""
        return self._params

    @params.setter
    def params(self, value):
        self._params = value

    def check(self):
        if 'datetime' not in self.params:
            self.params['datetime'] = ephem.now()
        if 'elevation' not in self.params:
            self.params['elevation'] = 0

        pdate = self.params['datetime']

        # Consts
        HORIZON_STANDARD = "-0.833"
        HORIZON_CIVIL = "-6"
        HORIZON_NAVAL = "-12"
        HORIZON_ASTRO = "-18"

        # Observer details
        obs = ephem.Observer()
        obs.lat = self.params['latitude']
        obs.long = self.params['longitude']
        obs.elevation = self.params['elevation']
        obs.date = self.params['datetime']

        # The sun
        sun=ephem.Sun(obs)
        sun.compute(obs)

        # Calc transit sun
        nexttransit = obs.next_transit(sun)
        prevtransit = obs.previous_transit(sun)

        if pdate.datetime().date() == nexttransit.datetime().date():
            obs.date = nexttransit

        if pdate.datetime().date() == prevtransit.datetime().date():
            obs.date = prevtransit

        # Standard
        obs.horizon = HORIZON_STANDARD
        sunrise_std = obs.previous_rising(sun)
        sunset_std  = obs.next_setting(sun)

        # Civil
        obs.horizon = HORIZON_CIVIL
        sunrise_civ = obs.previous_rising(sun)
        sunset_civ  = obs.next_setting(sun)

        # Nav
        obs.horizon = HORIZON_NAVAL
        sunrise_nav = obs.previous_rising(sun)
        sunset_nav  = obs.next_setting(sun)

        # Astro
        obs.horizon = HORIZON_ASTRO
        sunrise_ast = obs.previous_rising(sun)
        sunset_ast  = obs.next_setting(sun)

        # print "Now          : %s" % pdate
        # print "Astro Sunsise: %s" % sunrise_ast
        # print "Naval Sunsise: %s" % sunrise_nav
        # print "Civil Sunsise: %s" % sunrise_civ
        # print "      Sunsise: %s" % sunrise_std

        # print "      Sunset : %s" % sunset_std
        # print "Civil Sunset : %s" % sunset_civ
        # print "Naval Sunset : %s" % sunset_nav
        # print "Astro Sunset : %s" % sunset_ast

        idx = -1
        if pdate < sunrise_ast or pdate > sunset_ast:
            # Night
            idx = 0

        if idx < 0 and (
                (pdate > sunrise_ast and pdate < sunrise_nav)
                or
                (pdate > sunset_nav and pdate < sunset_ast)
        ):
            # Astronomic
            idx = 1

        if idx < 0 and (
                (pdate > sunrise_nav and pdate < sunrise_civ)
                or
                (pdate > sunset_civ and pdate < sunset_nav)
        ):
            # Naval
            idx = 2

        if idx < 0 and (
                (pdate > sunrise_civ and pdate < sunrise_std)
                or
                (pdate > sunset_std and pdate < sunset_civ)
        ):
            # Civil
            idx = 3


        if idx < 0 and pdate > sunrise_std and pdate < sunset_std:
            # Day
            idx = 255

        self.results['result'] = idx
