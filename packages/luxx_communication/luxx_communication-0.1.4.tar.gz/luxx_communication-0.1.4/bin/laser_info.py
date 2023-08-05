#!/usr/bin/env python
# -*- coding: utf-8 -*-

from luxx_communication import Laser

port = "/dev/ttyUSB0"
laser = Laser(port=port)

data = """
INFORMATION ABOUT CONNECTED LASER
=================================

Model:      %s
Serial:     %s
Wavelength: %.1f nm
Maximum power: %.1f mW
Working hours: %s
Serial port: %s
"""

print data % (laser.firmware, laser.serial, laser.wavelength,
                                    laser.pmax, laser.hours, laser.port.name)
del laser