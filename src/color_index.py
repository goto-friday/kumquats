#!/usr/bin/env python3

# TODO might be binning points twice; only needed once.

import os
import csv
import json
import math as m
import subprocess as sp

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({'font.size': 14})

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
        mag = avg_near(phase, 'mag', d)
        if mag == 0:
            break
        pt[d['filter']] = mag
    else:
        pts[phase] = pt

def mean(x):
    return sum(x)/len(x)

i = 0
pts2 = {}
while i < 1:
    close_pts = list(filter(lambda p: abs(p-i) < 0.05, pts))
    if len(close_pts) > 0:
        pts2[i] = {}
        for filt in pts[next(iter(pts))]:
            pts2[i][filt] = mean([pts[p][filt] for p in close_pts])
        #pts2[i] = [pts[p] for p in close_pts]
    i += 0.05

# Calculate the color index for each pair of filters (A, B) as
# A_mag - B_mag and plot it.

d={'B-V': []}
for p in pts2:
    d['B-V'].append((p, pts2[p]['B'] - pts2[p]['V']))

for i in range(len(c['filters'])-2):
    f1 = c['filters'][i]
    for j in range(i+2, len(c['filters'])):
        f2 = c['filters'][j]
        name = f1 + '-' + f2
        if name not in d:
            d[name] = []
        for p in pts2:
            d[name].append((p, pts2[p][f1] - pts2[p][f2]))

#fig, axes = plt.subplots(1, len(d))
#for ax in axes:
#    ax.invert_yaxis()
#fig, ax = plt.subplots()

os.makedirs("img/color", exist_ok=True)
max_index = max([max([x[1] for x in d[c]]) for c in d])
min_index = min([min([x[1] for x in d[c]]) for c in d])
fig, ax = plt.subplots()
ax.set_xlabel("Phase")
ax.set_ylabel("Color Index")

for i, comb in enumerate(d):
    d[comb].sort()
    phases = list(map(lambda x: x[0], d[comb]))
    indices = list(map(lambda x: x[1], d[comb]))
    colors = list(map(lambda x: [(x-min_index)/(max_index-min_index), 0,
        1-(x-min_index)/(max_index-min_index)], indices))
    #ax.scatter(phases, indices, c=colors, label=comb)
    ax.plot(phases, indices, label=comb)

ax.legend(fontsize=10, loc='upper right', ncols=4, bbox_to_anchor=(1, 1, 0, .14), borderaxespad=0)
fig.savefig("/tmp/ci.png")
