#!/usr/bin/env python3

import json
import csv
import math as m
import itertools as it

import yaml
import matplotlib.pyplot as plt
import lightkurve as lk

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
period = json.load(open("dat/period.json"))['period']
epoch = known[c['target']]['vsx']['Epoch']
dat = {}

for filt in c['filters']:
    dat[filt] = []
    for row in it.islice(csv.reader(open(f"dat/{filt}.csv")), 1, None):
        dat[filt].append({'phase': float(row[1]), 'mag': float(row[5])})
        #dat[filt].append({'x': row[1], 'mag': row[5]})
    #dat[filt] = sorted(dat[filt], key=lambda x: x['x'])
    dat[filt] = sorted(dat[filt], key=lambda x: x['phase'])

fig, ax = plt.subplots()
ax.invert_yaxis()
ax.set_xlabel("Phase")
ax.set_ylabel("Magnitude")
ax.tick_params(top=True, right=True, direction='in')
markers = [2, 'o', 's', '^', 3]

for i, filt in enumerate(dat):
    ax.plot([x['phase'] for x in dat[filt]], [x['mag'] for x in dat[filt]],
        label=f'{filt} Filter', marker=markers[i], markersize=5)

ax.legend(loc='upper right', ncols=3, bbox_to_anchor=(1, 1, 0, .14),
    borderaxespad=0, fontsize=10)
fig.savefig("img/lightcurves/all.png")
