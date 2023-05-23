#!/usr/bin/env python3

import json
import csv
import math as m
import itertools as it

import yaml
import matplotlib.pyplot as plt
import lightkurve as lk

plt.rcParams.update({'lines.markersize': 5})

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
period = json.load(open("dat/period.json"))['period']
epoch = known[c['target']]['vsx']['Epoch']
dat = {}

for filt in c['filters']:
    d = it.islice(csv.reader(open(f"dat/{filt}.csv")), 1, None)
    d = [dict(phase=float(r[1]), mag=float(r[5])) for r in d]
    dat[filt] = sorted(d, key=lambda x: x['phase'])

def new_plot():
    fig, ax = plt.subplots()
    ax.invert_yaxis()
    ax.set_xlabel("Phase")
    ax.set_ylabel("Magnitude")
    return fig, ax

fig, ax = new_plot()
markers = [2, 'o', 's', '^', 3]

for i, filt in enumerate(dat):
    phases, mags = [[x[k] for x in dat[filt]] for k in ('phase', 'mag')]
    ax.plot(phases, mags, label=f"{filt} Filter", marker=markers[i])

    fig2, ax2 = new_plot()
    ax2.set_title(f"{filt} Filter")
    ax2.scatter(phases, mags)
    fig2.savefig(f"img/lightcurves/{filt}.png")

ax.legend(loc='upper right', ncols=3, bbox_to_anchor=(1, 1, 0, .14),
    borderaxespad=0, fontsize=10)
fig.savefig("img/lightcurves/all.png")
