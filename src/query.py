#!/usr/bin/env python3

import json
import re
from urllib import request
from urllib.parse import quote_plus

import yaml
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier

Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)

def isnumber(x):
    try:
        float(x)
    except ValueError:
        return False
    return True

def denumpy(x):
    if np.ma.isMA(x):
        return None
    elif isinstance(x, np.generic):
        return x.item()
    else:
        return x

def closest(dat, *pairs):
    d = filter(lambda r: not any([np.ma.isMA(r[b]) for _, b in pairs]), dat)
    return sorted(d, key=lambda r:
        sum([1-abs(a-r[b])/max(a, r[b]) for a, b in pairs]))[-1]

def row_to_dict(r):
    return {k: denumpy(v) for k, v in zip(r.keys(), r.values())}

print(c['target'])
url = "https://www.aavso.org/vsx/index.php?view=api.object&format=json&ident=" \
    + quote_plus(c['target'])
vsx = json.load(request.urlopen(url))['VSXObject']
vsx['MaxMag'] = re.match("^[0-9.+-]+", vsx['MaxMag']).group(0)
vsx['MinMag'] = re.match("^[0-9.+-]+", vsx['MinMag']).group(0)

coords = SkyCoord(vsx['RA2000'], vsx['Declination2000'], unit='deg')
gaia = Gaia.query_object(coords, radius=.02*u.deg)
# mag is inversely proportional to brightness, hence the reversed test
gaia = filter(lambda r: r['phot_g_mean_mag'] >= float(vsx['MaxMag']) and
    r['phot_g_mean_mag'] <= float(vsx['MinMag']), gaia)
gaia = row_to_dict(closest(gaia, (float(vsx['RA2000']), 'ra'),
    (float(vsx['Declination2000']), 'dec')))

dat = {
    c['target']: {
        'vsx': {k: float(v) if isnumber(v) else v
            for k, v in zip(vsx.keys(), vsx.values())},
        'gaiadr3': gaia,
    },
    'comps': []
}

url = f"https://app.aavso.org/vsp/api/chart?ra={gaia['ra']}&dec={gaia['dec']}&fov=30&maglimit=14&format=json"
vsp = json.load(request.urlopen(url))['photometry']

# Query data from APASS9 for VSP's suggested comp stars
for comp in vsp:
    comp_name = "Comp " + comp['label']
    print(comp_name)
    dat['comps'].append(comp_name)

    coords = SkyCoord(comp['ra'], comp['dec'], unit=(u.hourangle, u.deg))
    ra, dec = coords.ra.value, coords.dec.value
    bmag = next(filter(lambda b: b['band'] == 'B', comp['bands']))['mag']
    vmag = next(filter(lambda b: b['band'] == 'V', comp['bands']))['mag']
    apass = Vizier.query_region(coords, radius=.02*u.deg,
        catalog='II/336/apass9')[0]
    apass = row_to_dict(closest(apass, (ra, 'RAJ2000'), (dec, 'DEJ2000'),
        (bmag, 'Bmag'), (vmag, 'Vmag')))
    apass['SGmag'], apass['e_SGmag'] = apass['g_mag'], apass['e_g_mag']
    apass['SRmag'], apass['e_SRmag'] = apass['r_mag'], apass['e_r_mag']
    apass['SImag'], apass['e_SImag'] = apass['i_mag'], apass['e_i_mag']
    gaia = row_to_dict(closest(Gaia.query_object(coords, radius=.02*u.deg),
        (ra, 'ra'), (dec, 'dec'), (apass['g_mag'], 'phot_g_mean_mag')))
    dat[comp_name] = {'apass9': apass, 'gaiadr3': gaia}

open("dat/known.json", 'w').write(json.dumps(dat))
