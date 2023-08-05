=========================
LuxX communication module
=========================

This module provides framework for communication with Omicron LuxX laser,
connected to the computer via serial interface (RS-232 or USB). You can
import it into your interpreter (e.g. IPython) and control laser with
simple self-explanatory statemens. Other option is to integrate it into
some kind of program, which allows flexible device control. Typical usage
often looks like this::

    #!/usr/bin/env python

    from luxx_communication import Laser

    laser = Laser(port="/dev/ttyUSB0")
    laser.set_power(10)         # 10 mW
    laser.set_mode("CW-ACC")    # Auto current control
    laser.start()               # Start light emission

Other Omicron lasers (BrixX and PhoxX) are controlled in a similar manner,
and this module should be able to control them right away. However, they
were never tested. These lasers have some additional functions, support
for which can be easily added into this module.

