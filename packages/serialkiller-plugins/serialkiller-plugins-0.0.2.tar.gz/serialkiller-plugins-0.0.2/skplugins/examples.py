#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2013 Bruno Adelé'
__description__ = """A plugins for serialkiller project"""
__license__ = 'GPL'
__version__ = '0.0.2'


import os
from daemon import runner
import time


from skplugins import addValuePlugin, addEventPlugin, addValue, addEvent
from skplugins.network.ping import ping
from skplugins.energy.teleinfo import teleinfo
from skplugins.weather.sunshine import sunshine

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/foo.pid'
        self.pidfile_timeout = 5

    def run(self):
        server = '192.168.1.1'

        while True:

            # Check internet connexion
            result = ping(destination="8.8.8.8", count=1)
            addValuePlugin(server, 'domsrv:network:available', result)


            # Check night
            result = sunshine(latitude="43:36:43", longitude="3:53:38", elevation=8)
            addValuePlugin(server, 'domsrv:weather:sunshine', result)

            # Check teleinfo informations
            # result = teleinfo(dev='/dev/teleinfo')
            # addValue(server, 'domsrv:teleinfo:hchc', result.types['HCHC'], result.results['HCHC'])
            # addValue(server, 'domsrv:teleinfo:hchp', result.types['HCHP'], result.results['HCHP'])
            # addValue(server, 'domsrv:teleinfo:iinst', result.types['IINST'], result.results['IINST'])
            # addValue(server, 'domsrv:teleinfo:imax', result.types['IMAX'], result.results['IMAX'])
            # addValue(server, 'domsrv:teleinfo:isousc', result.types['ISOUSC'], result.results['ISOUSC'])
            # addValue(server, 'domsrv:teleinfo:papp', result.types['PAPP'], result.results['PAPP'])

            #Sleep
            time.sleep(5)

# Launch in daemon mode
app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
