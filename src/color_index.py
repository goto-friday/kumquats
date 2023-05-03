#!/usr/bin/env python3

import os
import csv
import json
import math as m
import subprocess as sp

import matplotlib.pyplot as plt

def readin(filt, mag_comp):
    ret = dict(filter=filt, phase=[], mag=[])
    for i, row in enumerate(csv.reader(open(f"dat/{filt}.csv"))):
        # row = [hjd, phase, targ_flux, comp1_flux, comp2_flux, mag]
        if i == 0: continue
        ret['phase'].append(float(row[1]))
        ret['mag'].append(float(row[5]))
    return ret

def avg_near(phase, key, dat):
    ret = []
    for i in range(len(dat['phase'])):
        if abs(phase - dat['phase'][i]) < 0.05:
            ret.append(dat[key][i])
    return sum(ret)/len(ret) if len(ret) > 0 else 0

# For each point p in the filter with the most points, iterate over the
# other filters, calculating the average magnitude of all points for that
# filter that are within 0.05 units of p's phase. Add these new points,
# along with p, to a new set of points. This gives a set of points with
# each point covering all filters.

c = json.load(open("dat/custom.json"))
known = json.load(open("dat/known.json"))
dat = sorted([readin(f, known[c['comp1']]['mags'][f])
    for f in c['filters']], key=lambda d: len(d['phase']), reverse=True)
pts = {}
max_mag = 0
for i in range(len(dat[0]['phase'])):
    phase = dat[0]['phase'][i]
    mag = dat[0]['mag'][i]
    filt = dat[0]['filter']
    pt = {filt: mag}

    for d in dat[1:]:
        # TODO maybe inline this
        mag = avg_near(phase, 'mag', d)
        if mag == 0:
            break
        pt[d['filter']] = mag
    else:
        pts[phase] = pt

# Calculate the color index for each pair of filters (A, B) as
# A_mag - B_mag and plot it.

d = {}
for i in range(len(c['filters'])-1):
    f1 = c['filters'][i]
    for j in range(i+1, len(c['filters'])):
        f2 = c['filters'][j]
        name = f1 + '-' + f2
        if name not in d:
            d[name] = []
        for p in pts:
            d[name].append((p, abs(pts[p][f1] - pts[p][f2])))
#fig, axes = plt.subplots(1, len(d))
#for ax in axes:
#    ax.invert_yaxis()
#fig, ax = plt.subplots()
max_index = 0
for comb in d:
    indices = list(map(lambda e: e[1], d[comb]))
    max_index = max(indices+[max_index])
os.makedirs("img/color", exist_ok=True)
for i, comb in enumerate(d):
    d[comb].sort()
    phases = list(map(lambda e: e[0], d[comb]))
    indices = list(map(lambda e: e[1], d[comb]))
    colors = list(map(lambda e: [e/max_index, 0, 1-e/max_index],
        indices))
    #axes[i].scatter(
    fig, ax = plt.subplots()
    ax.set_ylim(0, 0.5)
    ax.set_xlim(0, 0.9)
    ax.set_xlabel("Phase")
    ax.set_ylabel("Color Index")
    ax.invert_yaxis()
    ax.scatter(phases, indices, c=colors)
    fig.savefig(f"img/color/{comb}.png")
# TODO make a single plot, see also todo.cgi?f=tommy
#for p in d[next(iter(d))]:
#    print(p)
#fig.savefig("/tmp/a.png")
