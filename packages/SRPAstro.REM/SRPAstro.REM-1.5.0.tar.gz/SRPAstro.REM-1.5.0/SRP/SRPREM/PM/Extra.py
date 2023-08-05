""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.1.0
Author  : Stefano Covino
Date    : 07/01/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (28/08/2012) First version.
        : (03/12/2013) Better naming.
        : (07/01/2014) Better organization of parameters.
"""

import numpy
from Full import Full


def Extra ((az,alt),(e_AAN,e_EAN,e_AAE,e_EAE,e_NPAE,e_BNP,e_AES,e_AEC,e_EES,e_EEC,e_AOFS,e_EOFS,e_ES2A,e_EC2A,e_ES3A,e_EC3A,e_C5)):
    # AAN: error in the leveling of the telescope toward north
    # AAE: error in the leveling of the telescope toward east
    # NPAE: non-perpendicularity of the azimuth and elevation axis
    # BNP: non-perpendicularity of the optical and the elevation axis
    # AES, AEC, EES, EEC:  eccentricity of the encoders
    # AOFS: azimuth zero point correction
    # EOFS: altitude zero point correction
    # EAN: Azimut axis at N of vertical (Elevation correction, = AAN)
    # AAE: Azimut axis at E of vertical (Azimut correction, = EAE)
    # ES2A = C1: Irregularities in the bearing race
    # EC2A = C2: Irregularities in the bearing race
    # ES3A = C3: Irregularities in the bearing race
    # EC3A = C4: Irregularities in the bearing race
    # C5: Empirical term
    # TF: Mechanic Flexure (= EEC)

    naz, nalt = Full((az,alt),(e_AAN,e_EAN,e_AAE,e_EAE,e_NPAE,e_BNP,e_AES,e_AEC,e_EES,e_EEC,e_AOFS,e_EOFS))
    nalt = nalt + e_ES2A * numpy.sin(numpy.radians(2*az)) + e_EC2A * numpy.cos(numpy.radians(2*az)) + e_ES3A * numpy.sin(numpy.radians(3*az)) + e_EC3A * numpy.cos(numpy.radians(3*az)) + e_C5 / numpy.cos(numpy.radians(alt))
    return naz, nalt

