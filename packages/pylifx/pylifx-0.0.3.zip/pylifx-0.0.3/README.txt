A Python library to control and monitor LIFX bulbs. Also provides a workaround
for users having issues with controlling LIFX bulbs on their network.

GitHub: https://github.com/derkarnold/pylifx
PyPi: https://pypi.python.org/pypi/pylifx

Originally written to allow the LIFX bulb to work in non-standard networks, but
it is growing to be much more.

Contributors: Deryck Arnold, Michael Farrell (micolous)

Huge thanks to Kevin Bowman(magicmonkey) and others for the lifxjs project on GitHub:
    https://github.com/magicmonkey/lifxjs/

Without their work on the lifxjs project, this one would not have been possible.

Current features:

  * Allows the LIFX bulb smartphone app to work by "faking" a bulb and relaying
    commands to the real one (see examples/bridge.py).
  * Gives the ability to display the contents of LIFX messages coming through.
    ** Huge thanks to magicmonkey and the lifxjs project for their hard work on
    working out the LIFX protocol.
  * The ability to run "scenes" - provide a dictionary of times and colours and
    the library will do the rest (see examples/sunrise.py).

Upcoming features:

  * Auto-discovery of bulbs (yes, should have been there already).
  * Support for more than one bulb per bridge (waiting on another bulb to arrive).

How to install:

  * Get Python (tested with 2.7, others may work). I use the Python(x, y) distribution.
  * Ensure you have the Python setuptools.
  * Run "easy_install pylifx" from a command prompt or terminal.
  * You're done.

Two common issues with installing:

  * Linux users - ensure you have python-dev installed (for the netifaces package).
  * Windows users - install the pre-built binaries for your python distribution
    using the links in the following URL: http://alastairs-place.net/projects/netifaces/
    (The section is just above the start of the Changelog section).