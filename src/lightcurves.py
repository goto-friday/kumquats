#!/usr/bin/env python3

import json
import csv
import math as m
import itertools as it

import yaml
import matplotlib.pyplot as plt

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
period = json.load(open("dat/period.json"))['period']
epoch = known[c['target']]['vsx']['Epoch']
dat = {}

for filt in c['filters']:
    d = it.islice(csv.reader(open(f"dat/{filt}.csv")), 1, None)
    d = [dict(phase=float(r[1]), mag=float(r[5])) for r in d]
    dat[filt] = sorted(d, key=lambda x: x['phase'])

tess = it.islice(csv.reader(open("dat/tess.csv")), 1, None)
tess = [dict(phase=float(r[1]), mag=float(r[2])) for r in tess]
tess = sorted(tess, key=lambda r: r['phase'])

asassn_g = it.islice(csv.reader(open("dat/asassn_g.csv")), 1, None)
asassn_g = [dict(phase=float(r[0]), mag=float(r[1])) for r in asassn_g]
asassn_g = sorted(asassn_g, key=lambda r: r['phase'])

asassn_v = it.islice(csv.reader(open("dat/asassn_v.csv")), 1, None)
asassn_v = [dict(phase=float(r[0]), mag=float(r[1])) for r in asassn_v]
asassn_v = sorted(asassn_v, key=lambda r: r['phase'])

def new_plot():
    fig, ax = plt.subplots(layout='constrained')
    ax.invert_yaxis()
    ax.set_xlabel("Phase")
    ax.set_ylabel("Magnitude")
    return fig, ax

fig, ax = new_plot()
markers = [2, 'o', 's', '^', 3]

for i, filt in enumerate(dat):
    phases = [x['phase'] for x in dat[filt]]
    mags = [x['mag'] for x in dat[filt]]
    ax.plot(phases, mags, label=filt, marker=markers[i])

    fig2, ax2 = new_plot()
    ax2.set_title(f"{filt} Filter")
    ax2.scatter(phases, mags)
    fig2.savefig(f"img/lightcurves/{filt}.png")

#ax.set_title("AAVSOnet")
fig.legend(loc='outside lower right', ncols=len(dat))
fig.savefig("img/lightcurves/all.png")

tess_phases = [r['phase'] for r in tess]
tess_mags = [r['mag'] for r in tess]

asassn_g_phases = [r['phase'] for r in asassn_g]
asassn_g_mags = [r['mag'] for r in asassn_g]

asassn_v_phases = [r['phase'] for r in asassn_v]
asassn_v_mags = [r['mag'] for r in asassn_v]

fig, ax = new_plot()
ax.scatter(tess_phases, tess_mags, s=2, label='TESS')
#ax.set_title("TESS")
fig.savefig("img/lightcurves/tess.png")

fig, ax = new_plot()
ax.scatter(asassn_g_phases, asassn_g_mags, s=6, marker='_',
    label='G Filter')
ax.scatter(asassn_v_phases, asassn_v_mags, s=6, marker='|',
    label='V Filter')
#ax.set_title("ASAS-SN")
fig.legend(loc='outside lower right', ncols=3)
fig.savefig("img/lightcurves/asassn.png")

fig, ax = new_plot()
ax.scatter(asassn_g_phases, asassn_g_mags, s=6, marker='_',
    label='ASAS-SN G')
ax.scatter(asassn_v_phases, asassn_v_mags, s=6, marker='|',
    label='ASAS-SN V')
ax.scatter(tess_phases, tess_mags, s=6, label='TESS')
#ax.set_title("ASAS-SN & TESS")
fig.legend(loc='outside lower right', ncols=3)
fig.savefig("img/lightcurves/asassn_tess.png")
