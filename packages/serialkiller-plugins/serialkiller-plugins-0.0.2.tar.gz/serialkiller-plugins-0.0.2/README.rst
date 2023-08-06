.. image:: https://travis-ci.org/badele/serialkiller-plugins.png?branch=master
   :target: https://travis-ci.org/badele/serialkiller-plugins

.. image:: https://coveralls.io/repos/badele/serialkiller-plugins/badge.png
   :target: https://coveralls.io/r/badele/serialkiller-plugins

.. disableimage:: https://pypip.in/v/serialkiller-plugins/badge.png
   :target: https://crate.io/packages/serialkiller-plugins/

.. disableimage:: https://pypip.in/d/serialkiller-plugins/badge.png
   :target: https://crate.io/packages/serialkiller-plugins/



About
=====

``serialkiller-plugins`` Plugins for serialkiller project


Installing
==========

To install the latest release from `PyPI <http://pypi.python.org/pypi/serialkiller-plugins>`_

.. code-block:: console

    $ pip install serialkiller-plugins

To install the latest development version from `GitHub <https://github.com/badele/serialkiller-plugins>`_

.. code-block:: console

    $ pip install git+git://github.com/badele/serialkiller-plugins.git

Plugins
=======
- Is online (ping)
- Teleinformation (French electric provider)
- Sunshine (calc sunrise & sunset)


Script example
==============

For checking the sensors periodically, i use the supervisor application, it can restart the application if it crashes.

Supervisor install.

.. code-block:: console

    # Debian
    $ apt-get install supervisor

    # Archlinux
    $ pacman -S supervisor

The check sensors supervisor configuration.

.. code-block:: console

    [program:check_sensors]
    command=~/.virtualenvs/serialkiller/bin/python /usr/local/bin/check_sensors.py
    user=badele
    autostart=true
    autorestart=true


Active and start supervisor.

.. code-block:: console

    # Debian
    $ /etc/init.d/supervisor start

    # Archlinux
    $ systemctl enable supvervisord
    $ systemctl start supvervisord

    # Show status
    $ supervisorctl status
    check_sensors                    RUNNING    pid 1306, uptime 23:48:04

``/usr/local/bin/check_sensors.py`` script example.

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    import os
    import time

    from skplugins import addValuePlugin, addEventPlugin, addValue, addEvent
    from skplugins.network.ping import ping
    from skplugins.weather.sunshine import sunshine

    server = '192.168.1.1'
    while True:

        # Check sunshine
        result = sunshine(latitude="43:36:43", longitude="3:53:38", elevation=8)
        addValuePlugin(server, 'city:weather:sunshine', result)

        # Check internet connexion
        result = ping(destination="8.8.8.8", count=1)
        addValuePlugin(server, 'livingroom:internet:available', result)

        # Check webcam
        result = ping(destination="192.168.1.2", count=1)
        addValuePlugin(server, 'livingroom:axis:online', result)

        # Check my computer
        result = ping(destination="192.168.1.3", count=1)
        addValuePlugin(server, 'bedroom:hp2012:online', result)

        # Check teleinfo informations
        result = teleinfo(dev='/dev/teleinfo')

        if 'HCHC' in result.results:
            addValue(server, 'washroom:teleinfo:hchc', result.types['HCHC'], result.results['HCHC'])

        if 'HCHP' in result.results:
            addValue(server, 'washroom:teleinfo:hchp', result.types['HCHP'], result.results['HCHP'])

        if 'IINST' in result.results:
            addValue(server, 'washroom:teleinfo:iinst', result.types['IINST'], result.results['IINST'])

        if 'ISOUSC' in result.results:
            addValue(server, 'washroom:teleinfo:isousc', result.types['ISOUSC'], result.results['ISOUSC'])

        if 'PAPP' in result.results:
            addValue(server, 'washroom:teleinfo:papp', result.types['PAPP'], result.results['PAPP'])

        #Sleep
        time.sleep(5)
