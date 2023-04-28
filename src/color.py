#!/usr/bin/env python3

import os
import csv
import math as m
import subprocess as sp
import matplotlib.pyplot as plt

#import lib

# flux_comp = [log10(flux_targ) - (mag_comp - mag_targ)/2.5]^10
def readin(filt, mag_comp):
    ret = dict(filter=filt, phase=[], mag=[], flux=[])
    for i, row in enumerate(csv.reader(open(f"dat/{filt}.csv"))):
        # row = [hjd, phase, targ_flux, comp1_flux, comp2_flux, mag]
        if i == 0: continue

        phase = float(row[1])
        flux_targ = float(row[3])
        mag = float(row[5])

        ret['phase'].append(phase)
        ret['mag'].append(mag)
        ret['flux'].append((m.log10(flux_targ) - (mag_comp - mag)/2.5)**10)
    return ret

def avg_near(phase, key, dat):
    ret = []
    for i in range(len(dat['phase'])):
        if abs(phase - dat['phase'][i]) < 0.05:
            ret.append(dat[key][i])
    return sum(ret)/len(ret) if len(ret) > 0 else 0

dat = sorted([
    readin("B", 11.967),
    readin("V", 11.644),
    readin("SR", 11.620)], 
    key = lambda x: len(x['phase']),
    reverse = True)

# TODO plot mag on a log scale (?)

pts = []
max_flux = 0
max_mag = 0
for i in range(len(dat[0]['phase'])):
    phase = dat[0]['phase'][i]
    mag = dat[0]['mag'][i]
    mag1 = avg_near(phase, 'mag', dat[1])
    mag2 = avg_near(phase, 'mag', dat[2])
    if mag1 == 0 or mag2 == 0:
        continue

    flux = dat[0]['flux'][i]
    flux1 = avg_near(phase, 'flux', dat[1])
    flux2 = avg_near(phase, 'flux', dat[2])
    max_flux = max(max_flux, flux, flux1, flux2)
    max_mag = max(max_mag, mag, mag1, mag2)
    pts.append(dict(
        phase = phase,
        avg_mag = (mag+mag1+mag2)/3,
        mags = {
            dat[0]['filter']: mag,
            dat[1]['filter']: mag1,
            dat[2]['filter']: mag2,
        }
    ))

pts.sort(key=lambda p: p['phase'])

d = dict(phases=[], mags=[], colors=[])
for i in range(len(pts)):
    d['phases'].append(pts[i]['phase'])
    d['mags'].append(pts[i]['avg_mag'])
    d['colors'].append((
        pts[i]['mags']['SR']/max_mag,
        pts[i]['mags']['V']/max_mag,
        pts[i]['mags']['B']/max_mag))

# TODO abstract
os.makedirs("img/color", exist_ok=True)

# Plot
# TODO abstract this into lib.py (e.g. plot(PNG, "color/plot"))
plt.xlabel("Phase")
plt.ylabel("Magnitude")
plt.gca().invert_yaxis()
plt.scatter('phases', 'mags', c='colors', data=d)
plt.savefig("img/color/plot.png")

# Animation
cmd = "magick -size 100x100 -delay 10".split()
for c in d['colors']:
    cmd.append("xc:rgb({},{},{})".format(c[0]*255, c[1]*255, c[2]*255))
cmd.append("img/color/animation.gif")
sp.run(cmd, check=True)
