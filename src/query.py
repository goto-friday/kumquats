#!/usr/bin/env python3

import sys
import os
sys.path.append(os.environ['HOME']+"/.local/lib/python3.10/site-packages")
sys.path.append("/usr/lib/python3.10/site-packages")

import json
import re
import astropy.units as u
from urllib import request
from urllib.parse import quote_plus

import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier

Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

c = json.load(open("dat/custom.json"))

url = "https://aavso.org/vsx/index.php?view=api.object&format=json&ident=" + quote_plus(c['target'])
vsx = json.load(request.urlopen(url))['VSXObject']
vsx_MaxMag = float(re.match("^[0-9.+-]+", vsx['MaxMag']).group(0))
vsx_MinMag = float(re.match("^[0-9.+-]+", vsx['MinMag']).group(0))

coords = SkyCoord(vsx['RA2000'], vsx['Declination2000'], unit='deg')
gaia = Gaia.query_object(coords, radius=.02*u.deg)
# mag is inversely proportional to brightness, hence the reversed test
gaia = filter(lambda r: r['phot_g_mean_mag'] >= float(vsx_MaxMag) and
    r['phot_g_mean_mag'] <= float(vsx_MinMag), gaia)
gaia = sorted(gaia, key=lambda r: sum([1-abs(a-b)/max(a, b) for a, b in
    ((float(vsx['RA2000']), r['ra']),
    (float(vsx['Declination2000']), r['dec']))]))[-1]

dat = {
    c['target']: {
        'ra': gaia['ra'],
        'dec': gaia['dec'],
        'pmra': gaia['pmra'],
        'pmdec': gaia['pmdec'],
        'period': float(vsx['Period']), # default type is str
        'gmag': float(gaia['phot_g_mean_mag']), # default type is np.float32
    }
}

url = f"https://app.aavso.org/vsp/api/chart?ra={gaia['ra']}&dec={gaia['dec']}&fov=30&maglimit=14&format=json"
vsp = json.load(request.urlopen(url))['photometry']

# Query data from APASS9 for VSP's suggested comp stars
for comp in vsp:
    coords = SkyCoord(comp['ra'], comp['dec'], unit=(u.hourangle, u.deg))
    ra, dec = coords.ra.value, coords.dec.value
    bmag, vmag = [[b['mag'] for b in comp['bands'] if b['band'] == F][0]
        for F in ('B', 'V')]
    d = Vizier.query_region(coords, radius=.02*u.deg,
        catalog='II/336/apass9').values()[0]
    rec = sorted(d, key=lambda r: sum([(1-abs(a-b)/max(a, b)) for a, b in
        ((ra, r['RAJ2000']), (dec, r['DEJ2000']),
        (bmag, r['Bmag']), (vmag, r['Vmag']))
            if str(r['Bmag']) != '--' and str(r['Vmag']) != '--']))[-1]
    dat['comp' + comp['label']] = {
        'ra': rec['RAJ2000'],
        'dec': rec['DEJ2000'],
        # `json` doesn't like the default type of numpy.float32
        'mags': {
            'B': float(rec['Bmag']),
            'eB': float(rec['e_Bmag']),
            'V': float(rec['Vmag']),
            'eV': float(rec['e_Vmag']),
            'SG': float(rec['g_mag']),
            'eSG': float(rec['e_g_mag']),
            'SI': float(rec['i_mag']),
            'eSI': float(rec['e_i_mag']),
            'SR': float(rec['r_mag']),
            'eSR': float(rec['e_r_mag']),
        }
    }

open("dat/known.json", 'w').write(json.dumps(dat))
