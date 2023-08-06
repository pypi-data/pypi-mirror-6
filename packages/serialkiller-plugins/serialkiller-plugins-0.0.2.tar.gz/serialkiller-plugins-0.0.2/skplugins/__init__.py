#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2013 Bruno Adelé'
__description__ = """A plugins for serialkiller project"""
__license__ = 'GPL'
__version__ = '0.0.2'
__apiversion__ = '1.0'

import os
import sys
import json
import requests
import time


class skplugins(object):
    """Generic Class for type"""
    def __init__(self, **kwargs):

        # Set parameters
        self._params = kwargs
        self._results = dict()
        self._types = dict()

    @property
    def params(self):
        """Get Value"""
        return self._params

    @params.setter
    def params(self, value):
        self._params = value

    @property
    def result(self):
        """Get Value"""
        if 'result' not in self.results:
            return None
        else:
            return self.results['result']

    @property
    def results(self):
        """Get Value"""
        return self._results

    @results.setter
    def results(self, value):
        """Set Value"""
        self._results = value

    @property
    def type(self):
        if 'result' not in self._types:
            raise Exception("type not found for result")

        return self._types['result']

    @property
    def types(self):
        return self._types

    def check(self):
        """Check Sensor"""
        # noinspection PyProtectedMember
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def getUrl(self, url):
        return requests.get(url)

    def getcachedresults(self):
        if 'cachefile' not in self.params:
            raise Exception("Not cachefile set")

        filename = self.params['cachefile']
        if 'cachetime' in self.params:
            cachetime = self.params['cachetime']
        else:
            cachetime = 1800

        if not os.path.exists(filename):
            # Cache not exists
            return None

        # Check if i use the cache results
        mtime = os.stat(filename).st_mtime
        now = time.time()
        if (now - mtime) > cachetime:
            # Cache is old
            return None

        # Use the cache file
        lines = open(filename).read()
        results = json.loads(lines)

        return results

    def setcacheresults(self):
        if 'cachefile' not in self.params:
            raise Exception("Not cachefile set")

        filename = self.params['cachefile']
        with open(filename, 'w') as f:
            jsontext = json.dumps(
                self.results, sort_keys=True,
                indent=4, separators=(',', ': ')
            )
            f.write(jsontext)
            f.close()


def addValuePlugin(server, sensorid, plugin):
    "Add value from plugin"""
    addValue(server, sensorid, plugin.type, plugin.result)


def addEventPlugin(server, sensorid, plugin):
    "Add event from plugin"""
    addEvent(server, sensorid, plugin.type, plugin.result)


def addValue(server, sensorid, ptype, value):
    "Add value from value"""
    url = 'addValue/%(sensorid)s/%(ptype)s/value=%(value)s' % locals()
    sendRequest(server, url)


def addEvent(server, sensorid, ptype, value):
    "Add event from value"""
    url = 'addValue/%(sensorid)s/%(ptype)s/value=%(value)s' % locals()
    sendRequest(server, url)


def sendRequest(server, request):
    apiversion = __apiversion__
    try:
        apiversion = __apiversion__
        url = "http://%(server)s/api/%(apiversion)s/%(request)s" % locals()
        requests.get(url)
        #print url
    except:
        pass
