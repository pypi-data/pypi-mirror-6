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

History : (28/08/2013) First version.
        : (03/12/2013) Better naming.
        : (07/01/2014) Better organization of parameters.
"""

from Extra import Extra
from SRP.SRPMath.FastAngularDistance import FastAngularDistance



def minExtra ((e_AAN,e_EAN,e_AAE,e_EAE,e_NPAE,e_BNP,e_AES,e_AEC,e_EES,e_EEC,e_AOFS,e_EOFS,e_ES2A,e_EC2A,e_ES3A,e_EC3A,e_C5),taz,talt,oaz,oalt):
    caz, calt = Extra((taz,talt),(e_AAN,e_EAN,e_AAE,e_EAE,e_NPAE,e_BNP,e_AES,e_AEC,e_EES,e_EEC,e_AOFS,e_EOFS,e_ES2A,e_EC2A,e_ES3A,e_EC3A,e_C5))
    return FastAngularDistance(oaz,oalt,caz,calt).sum()

