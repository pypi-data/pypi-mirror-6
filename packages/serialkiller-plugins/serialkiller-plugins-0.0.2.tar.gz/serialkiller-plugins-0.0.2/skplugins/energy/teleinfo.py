#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2013 Bruno Adelé'
__description__ = """A plugins for serialkiller project"""
__license__ = 'GPL'
__version__ = '0.0.2'

from skplugins import skplugins

import serial


class teleinfo(skplugins):
    """Get teleinfo information"""
    def __init__(self, **kwargs):
        super(teleinfo, self).__init__(**kwargs)
        self._types = {
            'HCHC': 'ulong',
            'HCHP': 'ulong',
            'IINST': 'byte',
            'IMAX': 'byte',
            'ISOUSC': 'byte',
            'PAPP': 'ushort',
            'result': 'ushort',
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
        if 'dev' not in self.params:
            self.params['dev'] = '/dev/teleinfo'

        tinfo = Teleinfo(self.params['dev'])
        self._results = tinfo.read()
        self._results ['result'] = self._results['PAPP']


class Teleinfo:
    # Source: http://code.google.com/p/teleinfofs/

    ser = serial.Serial()

    def __init__(self, port='/dev/ttyS2'):
        self.ser = serial.Serial(port, baudrate=1200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN)

    def checksum(self, etiquette, valeur):
        sum = 32
        for c in etiquette: sum = sum + ord(c)
        for c in valeur: sum = sum + ord(c)
        sum = (sum & 63) + 32
        return chr(sum)

    def read(self):
        # Attendre le debut du message
        while self.ser.read(1) != chr(2): pass

        message = ""
        fin = False

        while not fin:
            char = self.ser.read(1)
            if char != chr(2):
                message = message + char
            else:
                fin = True

        trames = [
            trame.split(" ")
            for trame in message.strip("\r\n\x03").split("\r\n")
            ]

        tramesValides = dict([
            [trame[0], trame[1]]
            for trame in trames
            if (len(trame) == 3) and (self.checksum(trame[0], trame[1]) == trame[2])
            ])

        return tramesValides
