#!/usr/bin/env python3

# TODO use astroquery directly
# TODO use `csv` lib

import json
import yaml
import lightkurve as lk

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
period = json.load(open("dat/period.json"))['period']
epoch = known[c['target']]['vsx']['Epoch']

d = lk.search_lightcurve(c['target'], mission='TESS',
    author=c['tess_pipeline'])[0].download()
phases = map(lambda t: (t - epoch)/period % 1, d['time'].value)

# CDIPS flux = mag
buf = "hjd,phase,mag\n"
for hjd, phase, mag in zip(d['time'].value, phases, d['flux'].value):
    buf += f"{hjd},{phase},{mag}\n"

open("dat/tess.csv", 'w').write(buf)
