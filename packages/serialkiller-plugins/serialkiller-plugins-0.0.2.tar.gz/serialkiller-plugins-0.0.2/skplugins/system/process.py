#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2013 Bruno Adelé'
__description__ = """A plugins for serialkiller project"""
__license__ = 'GPL'
__version__ = '0.0.2'

from subprocess import *

from skplugins import skplugins


class process(skplugins):
    """Check if process exist"""
    def __init__(self, **kwargs):
        super(process, self).__init__(**kwargs)
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

    def getProcessIDs(self, processname):
        cmd = 'pidof "%s"' % processname

        pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = pipe.read().strip()

        if len(output) == 0:
            return []

        processids = output.split(' ')
        return processids

    def check(self):
        """Check if process running"""
        if 'processname' not in self.params:
            self.results['result'] = None
            return

        self.results['result'] = 0
        if len(self.getProcessIDs(self.params['processname'])) > 0:
            self.results['result'] = 255
