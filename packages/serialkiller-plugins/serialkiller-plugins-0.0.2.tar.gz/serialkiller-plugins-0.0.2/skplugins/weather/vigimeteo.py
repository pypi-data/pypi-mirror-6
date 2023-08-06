#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2013 Bruno Adelé'
__description__ = """A plugins for serialkiller project"""
__license__ = 'GPL'
__version__ = '0.0.2'

import re
from skplugins import skplugins


class vigimeteo(skplugins):
    """Check the vigilance of meteofrance.fr"""
    def __init__(self, **kwargs):
        super(vigimeteo, self).__init__(**kwargs)
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

    def checkVigimeteo(self, dep):
        results = self.getcachedresults()

        # Result not cached
        if results:
            self.results = results
        else:
            r = self.getUrl("http://vigilance.meteofrance.com/data/NXFR34_LFPW_.xml")

            if r.status_code != 200:
                return None

            # Get departement vigilance status
            m = re.search(
                '<datavigilance couleur="([0-9])" dep="%s">.*?</datavigilance>' % self.params['dep'],
                r.content
            )

            if not m:
                return None

            depalert = m.group(0)

            # Check vigilance
            m = re.search('<datavigilance couleur="([0-9])"', depalert)
            if m:
                self.results['result'] = int(m.group(1))

            # Check crue
            m = re.search('<crue valeur="([0-9])"', depalert)
            if m:
                self.results['crue'] = int(m.group(1))

            # Check risque
            m = re.search('<risque valeur="([0-9])"', depalert)
            if m:
                self.results['risque'] = int(m.group(1))

            # Save results
            self.setcacheresults()

    def check(self):
        """Check if process running"""
        if 'dep' not in self.params:
            self.results['result'] = None
            return

        self.checkVigimeteo(self.params['dep'])
