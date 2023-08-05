#!/usr/bin/env python
# -*- coding: utf-8 -*-

from luxx_communication import Laser

port = "/dev/ttyUSB0"
laser = Laser(port=port)

laser.set_mode("CW-ACC")
laser.set_power(0.1*laser.pmax)
laser.set_autostart(True)
laser.start()

del laser