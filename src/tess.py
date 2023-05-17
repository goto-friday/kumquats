#!/usr/bin/env python3

# TODO use astroquery directly
import json
import yaml
import lightkurve as lk
import matplotlib.pyplot as plt

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
period = json.load(open("dat/period.json"))['period']
epoch = known[c['target']]['vsx']['Epoch']

d = lk.search_lightcurve(c['target'], mission='TESS',
    author=c['tess_pipeline'])[0].download()
phases = map(lambda t: (t - epoch)/period % 1, d['time'].value)
mags = d['flux'].value
dat = sorted(zip(phases, mags), key=lambda x: x[0])
phases = [x[0] for x in dat]
mags = [x[1] for x in dat]

fig, ax = plt.subplots()
ax.invert_yaxis()
ax.set_xlabel("Phase")
ax.set_ylabel("Magnitude")
ax.scatter(phases, mags, s=2, label='TESS')
fig.savefig("img/lightcurves/tess.png")
