#!/usr/bin/env python3

import json
import csv
import math as m
import itertools as it

import yaml
import matplotlib as mpl
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
fig.savefig("img/lightcurve.png")

exit()
# TODO move everything below to a new file

fig, ax = plt.subplots()
ax.invert_yaxis()
ax.set_xlabel("Phase")
ax.set_ylabel("Magnitude")
ax.tick_params(top=True, right=True, direction='in')

# TODO move to query.py
# TODO use astroquery directly?
# TODO don't limit to CDIPS (currently doing so b/c
# it's the only one that gives mag)
d = lk.search_lightcurve(c['target'], mission='TESS', author='CDIPS')[0] \
    .download()
phases = list(map(lambda t: ((t - epoch)/period)%1,
    d['time'].value))
mags = d['flux'].value  # XXX flux appears to be equal to mag here?
dat = sorted(zip(phases, mags), key=lambda x: x[0])
phases = [x[0] for x in dat]
mags = [x[1] for x in dat]
#for i in range(len(phases)):
#    print(phases[i], mags[i])
ax.scatter(phases, mags, s=2, label='TESS')

fig.savefig("/tmp/c.png")

fig, ax = plt.subplots()
ax.invert_yaxis()
ax.set_xlabel("Phase")
ax.set_ylabel("Magnitude")
ax.tick_params(top=True, right=True, direction='in')

# TODO actually generate the csv files from something
# TODO clean up this horrible mess
dat=sorted(map(lambda x: (float(x[0].split()[0]), float(x[0].split()[1])),
    it.islice(csv.reader(open("dat/ASASSN_G.csv")), 1, None)),
    key=lambda x: x[0])
ax.scatter([x[0] for x in dat], [x[1] for x in dat], s=6,
    label='ASAS-SN G Filter', marker='_')
dat=sorted(map(lambda x: (float(x[0].split()[0]), float(x[0].split()[1])),
    it.islice(csv.reader(open("dat/ASASSN_V.csv")), 1, None)),
    key=lambda x: x[0])
ax.scatter([x[0] for x in dat], [x[1] for x in dat], s=6,
    label='ASAS-SN V Filter', marker='|')

ax.legend(loc='upper right', ncols=3, bbox_to_anchor=(1, 1, 0, .09), borderaxespad=0, fontsize=10)
fig.savefig("/tmp/b.png")
