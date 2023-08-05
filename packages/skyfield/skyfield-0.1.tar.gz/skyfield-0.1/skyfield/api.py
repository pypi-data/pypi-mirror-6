"""Top-level objects and functions offered by the Skyfield library.

Importing this ``skyfield.api`` module causes Skyfield to load up the
default JPL planetary ephemeris ``de421`` and create planet objects like
``earth`` and ``mars`` that are ready for your use.

"""
import de421
from datetime import datetime
from .jpllib import Ephemeris
from .timelib import JulianDate, now, utc

ephemeris = Ephemeris(de421)
del Ephemeris

sun = ephemeris.sun
mercury = ephemeris.mercury
venus = ephemeris.venus
earth = ephemeris.earth
moon = ephemeris.moon
mars = ephemeris.mars
jupiter = ephemeris.jupiter
saturn = ephemeris.saturn
uranus = ephemeris.uranus
neptune = ephemeris.neptune
pluto = ephemeris.pluto

eight_planets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]
nine_planets = eight_planets + [pluto]
