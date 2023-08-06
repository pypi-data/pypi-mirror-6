#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2013 Bruno Adelé'
__description__ = """A plugins for serialkiller project"""
__license__ = 'GPL'
__version__ = '0.0.2'

from skplugins import skplugins

import pyping


class ping(skplugins):
    """Check if host reply a ICMP request"""
    def __init__(self, **kwargs):
        super(ping, self).__init__(**kwargs)
        self._types = {
            'result': 'boolean',
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
        if 'timeout' not in self.params:
            self.params['timeout'] = 5000
        if 'count' not in self.params:
            self.params['count'] = 2

        r = pyping.ping(
            hostname=self.params['destination'],
            timeout=self.params['timeout'],
            count=self.params['count'],
        )
        self._results = {
            'max_rtt': r.max_rtt,
            'min_rtt': r.min_rtt,
            'avg_rtt': r.avg_rtt,
            'packet_lost': r.packet_lost,
            'output': r.output,
            'packet_size': r.packet_size,
            'timeout': r.timeout,
            'destination': r.destination,
            'destination_ip': r.destination_ip,
            'result': 255 - (r.ret_code * 255),
        }
