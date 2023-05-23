#!/usr/bin/env python3

import json
import re
import sys

import yaml
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astroquery.gaia import Gaia

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))

main_fns = []
def main(f):
    main_fns.append(f)
    return f


"""
c['eclipses'][eclipses[i]]['start'] - c['eclipses'][eclipses[i]]['end']
c['eclipses'][eclipses[i]]['end'] - c['eclipses'][eclipses[i+1]]['start']
c['eclipses'][eclipses[i+1]]['start'] - c['eclipses'][eclipses[i+1]]['end']

@main
def mag_drop():
    # WRONG
    # First step: sort eclipses by start time, then fill in the blanks for
    # times of no eclipse, possibly similar to below code.
    ecls = c['eclipses']
    ecl_names = list(c['eclipses'].keys())
    for i in range(len(ecls)-1):
        if i > 0:
            compare(ecls[ecl_names[i-1]]['end'],
                ecls[ecl_names[i]]['start'])
        compare(ecls[ecl_names[i]]['start'], ecls[ecl_names[i]]['end'])

    # Calculate the average magnitude drop precisely. (See
    # the paper comment on page 13)
    print("mag_drop")
"""

@main
def red_giants():
    # Get pertinent mag ranges from isochrone (and store
    # in custom.yaml), search gaia for these, and use the
    # ra/dec from gaia to locate the star in the image.
    # (Do we even need to do the last part? Maybe it's
    # sufficient to just note the color from gaia or
    # something)
    r = VizieR(row_limit=100, catalog='I/355/gaiadr3').query_region(coords,
        radius=2*u.arcmin, column_filters={'BP-RP': '1.75 ... 2.0'})[0]
    print("red_giants")

def pm(a, b):
    return f"{a:.3f} \u00B1 {b:.3f}"

@main
def table1():
    t = {k: [] for k in ['Name', 'Coordinates', 'PM', 'Gmag', 'Parallax']}
    for star in ['target', 'comp', 'check']:
        gaia = known[c[star]]['gaiadr3']
        crds = SkyCoord(gaia['ra'], gaia['dec'], unit='deg')
        plx, eplx = gaia['parallax'], gaia['parallax_error']
        pmra, epmra = gaia['pmra'], gaia['pmra_error']
        pmdec, epmdec = gaia['pmdec'], gaia['pmdec_error']

        t['Name'].append(c[star])
        t['Coordinates'].append(crds.to_string('hmsdms', precision=2,
            sep=' '))
        t['PM'].append(f"{pm(pmra, epmra)}, {pm(pmdec, epmdec)}")
        t['Gmag'].append(round(gaia['phot_g_mean_mag'], 3))
        t['Parallax'].append(pm(plx, eplx))
    Table(t).pprint_all()


if len(sys.argv) > 1:
    for f in sys.argv[1:]:
        if not re.fullmatch('\w+', sys.argv[1]):
            exit(f"bad format: '{f}'")
        eval(f)()
else:
    with open("out/info.txt", 'w') as sys.stdout:
        for f in main_fns:
            print(f"\n=== {f.__name__}() ===\n")
            f()
