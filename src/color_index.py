#!/usr/bin/env python3

import os
import csv
import json
import yaml
import itertools as it

import matplotlib.pyplot as plt

def readin(filt, mag_comp):
    return [dict(phase=float(row[1]), mag=float(row[5]))
        for row in it.islice(csv.reader(open(f"dat/{filt}.csv")), 1, None)]

def mean(x):
    return len(x) and sum(x)/len(x)

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
dat = {filt: readin(filt, known[c['comp']]['apass9'][filt+'mag'])
    for filt in c['filters']}

def combo(pts, f1, f2):
    n_pts = len(list(it.chain(*[pts[p][f1] + pts[p][f2] for p in pts])))
    f_pts = [dict(phase=p, cidx=mean(pts[p][f1]) - mean(pts[p][f2]))
        for p in pts if len(pts[p][f1]) > 0 and len(pts[p][f2]) > 0]
    return dict(npts=n_pts, pts=f_pts)

def bin(dat):
    # To include all filters, change 2 to 1 in both loops below
    filts = list(dat[next(iter(dat))].keys())
    ret = {'B-V': combo(dat, 'B', 'V')}
    for i in range(len(filts)-2):
        f1 = filts[i]
        for j in range(i+2, len(filts)):
            f2 = filts[j]
            ret[f1+'-'+f2] = combo(dat, f1, f2)
    return ret

pts = {}
for i in [x/10 for x in range(0, 11)]:
    pts[i] = {}
    for filt in dat:
        pts[i][filt] = [p['mag'] for p in dat[filt]
            if i-0.05 < p['phase'] <= i+0.05]
d = bin(pts)

min_pts = min([d[c]['npts'] for c in d])
max_pts = max([d[c]['npts'] for c in d])

fig, axs = plt.subplots(1, 2, sharey=True)
axs[0].set_xlabel("Phase")
axs[0].set_ylabel("Color Index")
axs[1].set_xlabel("Eclipse")
markers = ['^', 'o', 2, 's', 3, 'd', 'v']

for i, comb in enumerate(d):
    phases = [x['phase'] for x in d[comb]['pts']]
    indices = [x['cidx'] for x in d[comb]['pts']]
    weight = (3*(d[comb]['npts']-min_pts))/(max_pts-min_pts) + 0.5
    axs[0].plot(phases, indices, label=comb, linewidth=weight,
        marker=markers[i], markersize=max(3, weight*3))

# TODO handle ranges of no eclipse
# TODO mirror
pts = {}
for ec in c['eclipses']:
    pts[ec] = {}
    for nec in c['eclipses'][ec]:
        for filt in dat:
            if filt not in pts[ec]:
                pts[ec][filt] = []
            pts[ec][filt] += [p['mag'] for p in dat[filt]
                if nec['start'] <= p['phase'] < nec['end']]

for i, comb in enumerate(d):
    phases = [x['phase'] for x in d[comb]['pts']]
    indices = [x['cidx'] for x in d[comb]['pts']]
    axs[1].plot(phases, indices, label=comb, marker = markers[i])

axs[1].legend(fontsize=10, loc='upper right', ncols=4,
    bbox_to_anchor=(1, 1, 0, .14), borderaxespad=0)
fig.savefig("img/color_index.png")
