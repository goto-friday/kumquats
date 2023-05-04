#!/usr/bin/env python3

import os
import csv
import json
import itertools as it

import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 12})

def readin(filt, mag_comp):
    return [dict(phase=float(row[1]), mag=float(row[5]))
        for row in it.islice(csv.reader(open(f"dat/{filt}.csv")), 1, None)]

def mean(x):
    return len(x) and sum(x)/len(x)

c = json.load(open("dat/custom.json"))
known = json.load(open("dat/known.json"))
dat = {f: readin(f, known[c['comp1']]['mags'][f]) for f in c['filters']}

pts = {}
for i in [x/10 for x in range(0, 11)]:
    pts[i] = {}
    for filt in dat:
        pts[i][filt] = [p['mag'] for p in dat[filt]
            if i-0.05 < p['phase'] <= i+0.05]

def combo(f1, f2):
    n_pts = len(list(it.chain(*[pts[p][f1] + pts[p][f2] for p in pts])))
    f_pts = [dict(phase=p, cidx=mean(pts[p][f1]) - mean(pts[p][f2]))
        for p in pts if len(pts[p][f1]) > 0 and len(pts[p][f2]) > 0]
    return dict(npts=n_pts, pts=f_pts)

# To include all filters, change 2 to 1 in both loops below
d = {'B-V': combo('B', 'V')}
for i in range(len(c['filters'])-2):
    f1 = c['filters'][i]
    for j in range(i+2, len(c['filters'])):
        f2 = c['filters'][j]
        d[f1+'-'+f2] = combo(f1, f2)

min_pts = min([d[c]['npts'] for c in d])
max_pts = max([d[c]['npts'] for c in d])

fig, ax = plt.subplots()
ax.set_xlabel("Phase")
ax.set_ylabel("Color Index")
ax.tick_params(top=True, right=True, direction='in')
markers = ['^', 'o', 2, 's', 3, 'd', 'v']

for i, comb in enumerate(d):
    phases = [x['phase'] for x in d[comb]['pts']]
    indices = [x['cidx'] for x in d[comb]['pts']]
    weight = (3*(d[comb]['npts']-min_pts))/(max_pts-min_pts) + 0.5
    ax.plot(phases, indices, label=comb, linewidth=weight,
        marker=markers[i], markersize=max(3, weight*3))

ax.legend(fontsize=10, loc='upper right', ncols=4,
    bbox_to_anchor=(1, 1, 0, .14), borderaxespad=0)
os.makedirs("img/color", exist_ok=True)
fig.savefig("img/color/index.png")
